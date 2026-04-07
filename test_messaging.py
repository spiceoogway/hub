"""
Tests for the extracted messaging module.

Covers: EventHook, agent registration, message send/receive,
inbox management, delivery tracking, liveness, and discovery.
Runs against a temp data directory — no live Hub needed.
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Ensure hub package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from hub.events import EventHook


# ══════════════════════════════════════════════════════════════════════
#  EventHook Tests
# ══════════════════════════════════════════════════════════════════════

class TestEventHook:
    def test_subscribe_and_fire(self):
        hook = EventHook()
        results = []
        hook.subscribe(lambda x: results.append(x))
        hook.fire("hello")
        assert results == ["hello"]

    def test_multiple_subscribers(self):
        hook = EventHook()
        log = []
        hook.subscribe(lambda x: log.append(f"a:{x}"))
        hook.subscribe(lambda x: log.append(f"b:{x}"))
        hook.fire("test")
        assert log == ["a:test", "b:test"]

    def test_fire_returns_non_none_results(self):
        hook = EventHook()
        hook.subscribe(lambda: "result1")
        hook.subscribe(lambda: None)
        hook.subscribe(lambda: {"key": "val"})
        results = hook.fire()
        assert results == ["result1", {"key": "val"}]

    def test_exception_doesnt_block_other_subscribers(self, capsys):
        hook = EventHook()
        log = []
        hook.subscribe(lambda: log.append("first"))

        def bad():
            raise ValueError("boom")

        hook.subscribe(bad)
        hook.subscribe(lambda: log.append("third"))
        hook.fire()
        assert log == ["first", "third"]
        captured = capsys.readouterr()
        assert "bad failed" in captured.out

    def test_clear(self):
        hook = EventHook()
        hook.subscribe(lambda: None)
        hook.subscribe(lambda: None)
        assert len(hook) == 2
        hook.clear()
        assert len(hook) == 0

    def test_decorator_pattern(self):
        hook = EventHook()

        @hook.subscribe
        def handler(x):
            return x * 2

        results = hook.fire(5)
        assert results == [10]


# ══════════════════════════════════════════════════════════════════════
#  Messaging Module Tests
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def msg_app():
    """Create a Flask app with messaging Blueprint and temp data dir."""
    from flask import Flask
    from flask_sock import Sock
    from hub.messaging import (
        messaging_bp, init_messaging, register_websocket,
        on_message_sent, on_agent_registered, on_message_read, on_agent_event,
    )

    tmpdir = tempfile.mkdtemp(prefix="hub-test-")

    app = Flask(__name__)
    app.config["TESTING"] = True
    sock = Sock(app)

    # Clear any previous subscribers from other tests
    on_message_sent.clear()
    on_agent_registered.clear()
    on_message_read.clear()
    on_agent_event.clear()

    init_messaging(Path(tmpdir))
    app.register_blueprint(messaging_bp)
    register_websocket(sock)

    yield app, tmpdir

    # Cleanup
    on_message_sent.clear()
    on_agent_registered.clear()
    on_message_read.clear()
    on_agent_event.clear()
    shutil.rmtree(tmpdir, ignore_errors=True)


class TestRegistration:
    def test_register_agent(self, msg_app):
        app, tmpdir = msg_app
        with app.test_client() as c:
            resp = c.post("/agents/register", json={
                "agent_id": "test-agent",
                "description": "A test agent",
                "capabilities": ["testing"]
            })
            data = resp.get_json()
            assert resp.status_code == 200
            assert data["ok"] is True
            assert data["agent_id"] == "test-agent"
            assert "secret" in data
            assert data["important"] == "SAVE your secret \u2014 it is returned ONCE."
            # Rich response includes setup instructions
            assert "option_1_callback" in data
            assert "option_2_cron" in data
            assert "option_3_websocket" in data

    def test_register_duplicate(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            c.post("/agents/register", json={"agent_id": "dupe"})
            resp = c.post("/agents/register", json={"agent_id": "dupe"})
            assert resp.status_code == 409

    def test_register_invalid_id(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            resp = c.post("/agents/register", json={"agent_id": "bad agent!"})
            assert resp.status_code == 400

    def test_register_fires_hook(self, msg_app):
        app, _ = msg_app
        from hub.messaging import on_agent_registered
        hook_log = []
        on_agent_registered.subscribe(
            lambda agent_id, record, data: hook_log.append(agent_id)
        )
        with app.test_client() as c:
            c.post("/agents/register", json={"agent_id": "hook-test"})
        assert hook_log == ["hook-test"]

    def test_register_hook_extras_in_response(self, msg_app):
        app, _ = msg_app
        from hub.messaging import on_agent_registered

        def add_extras(agent_id, record, data):
            return {"hub_balance": 100, "hub_token": "TOKEN123"}

        on_agent_registered.subscribe(add_extras)
        with app.test_client() as c:
            resp = c.post("/agents/register", json={"agent_id": "extras-test"})
            data = resp.get_json()
            assert data["hub_balance"] == 100
            assert data["hub_token"] == "TOKEN123"

    def test_welcome_message_in_inbox(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            reg = c.post("/agents/register", json={"agent_id": "inbox-check"}).get_json()
            secret = reg["secret"]
            inbox = c.get(f"/agents/inbox-check/messages?secret={secret}").get_json()
            assert inbox["count"] == 1
            assert "welcome" in inbox["messages"][0]["id"]


class TestSendMessage:
    def _register(self, client, agent_id):
        resp = client.post("/agents/register", json={"agent_id": agent_id})
        return resp.get_json()["secret"]

    def test_send_and_receive(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s1 = self._register(c, "sender")
            s2 = self._register(c, "receiver")

            resp = c.post("/agents/receiver/message", json={
                "from": "sender",
                "secret": s1,
                "message": "Hello receiver!"
            })
            data = resp.get_json()
            assert data["ok"] is True
            assert "message_id" in data
            assert data["delivered_to_inbox"] is True

            # Check receiver inbox
            inbox = c.get(f"/agents/receiver/messages?secret={s2}").get_json()
            # 1 welcome + 1 message
            msgs = [m for m in inbox["messages"] if m.get("from") == "sender"]
            assert len(msgs) == 1
            assert msgs[0]["message"] == "Hello receiver!"

    def test_send_fires_hook(self, msg_app):
        app, _ = msg_app
        from hub.messaging import on_message_sent
        hook_log = []
        on_message_sent.subscribe(
            lambda sender, recipient, msg: hook_log.append((sender, recipient))
        )
        with app.test_client() as c:
            s = self._register(c, "alice")
            self._register(c, "bob")
            c.post("/agents/bob/message", json={
                "from": "alice", "secret": s, "message": "hi"
            })
        assert hook_log == [("alice", "bob")]

    def test_send_no_auth(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            self._register(c, "authed")
            self._register(c, "target")
            resp = c.post("/agents/target/message", json={
                "from": "authed", "message": "no secret"
            })
            assert resp.status_code == 401

    def test_send_wrong_secret(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            self._register(c, "wrongsec")
            self._register(c, "target2")
            resp = c.post("/agents/target2/message", json={
                "from": "wrongsec", "secret": "bad", "message": "hi"
            })
            assert resp.status_code == 403

    def test_send_to_nonexistent(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s = self._register(c, "orphan")
            resp = c.post("/agents/nobody/message", json={
                "from": "orphan", "secret": s, "message": "hi"
            })
            assert resp.status_code == 404

    def test_topic_and_reply_to(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s1 = self._register(c, "topicsender")
            s2 = self._register(c, "topicreceiver")
            resp = c.post("/agents/topicreceiver/message", json={
                "from": "topicsender",
                "secret": s1,
                "message": "threaded msg",
                "topic": "project-x",
                "reply_to": "msg-000"
            })
            data = resp.get_json()
            assert data["ok"]

            inbox = c.get(f"/agents/topicreceiver/messages?secret={s2}&topic=project-x").get_json()
            thread_msgs = [m for m in inbox["messages"] if m.get("topic") == "project-x"]
            assert len(thread_msgs) == 1
            assert thread_msgs[0]["reply_to"] == "msg-000"


class TestMarkRead:
    def _setup(self, client):
        s1 = client.post("/agents/register", json={"agent_id": "reader"}).get_json()["secret"]
        s2 = client.post("/agents/register", json={"agent_id": "writer"}).get_json()["secret"]
        client.post("/agents/reader/message", json={
            "from": "writer", "secret": s2, "message": "read me"
        })
        return s1, s2

    def test_mark_read(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s1, _ = self._setup(c)
            inbox = c.get(f"/agents/reader/messages?secret={s1}").get_json()
            msg = [m for m in inbox["messages"] if m["from"] == "writer"][0]
            assert msg["read"] is False

            resp = c.post(f"/agents/reader/messages/{msg['id']}/read?secret={s1}")
            assert resp.get_json()["ok"] is True

            inbox2 = c.get(f"/agents/reader/messages?secret={s1}").get_json()
            msg2 = [m for m in inbox2["messages"] if m["id"] == msg["id"]][0]
            assert msg2["read"] is True

    def test_mark_read_fires_hook(self, msg_app):
        app, _ = msg_app
        from hub.messaging import on_message_read
        hook_log = []
        on_message_read.subscribe(
            lambda agent_id, message_id, sender_id: hook_log.append(agent_id)
        )
        with app.test_client() as c:
            s1, _ = self._setup(c)
            inbox = c.get(f"/agents/reader/messages?secret={s1}").get_json()
            msg = [m for m in inbox["messages"] if m["from"] == "writer"][0]
            c.post(f"/agents/reader/messages/{msg['id']}/read?secret={s1}")
        assert hook_log == ["reader"]


class TestInboxManagement:
    def _setup(self, client):
        s = client.post("/agents/register", json={"agent_id": "mgmt"}).get_json()["secret"]
        s2 = client.post("/agents/register", json={"agent_id": "sender"}).get_json()["secret"]
        client.post("/agents/mgmt/message", json={
            "from": "sender", "secret": s2, "message": "msg1"
        })
        client.post("/agents/mgmt/message", json={
            "from": "sender", "secret": s2, "message": "msg2"
        })
        return s, s2

    def test_delete_message(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s, _ = self._setup(c)
            inbox = c.get(f"/agents/mgmt/messages?secret={s}").get_json()
            # Find a non-welcome message
            msgs = [m for m in inbox["messages"] if m["from"] == "sender"]
            msg_id = msgs[0]["id"]

            resp = c.delete(f"/agents/mgmt/messages/{msg_id}?secret={s}")
            assert resp.get_json()["ok"] is True

            inbox2 = c.get(f"/agents/mgmt/messages?secret={s}").get_json()
            remaining_ids = [m["id"] for m in inbox2["messages"]]
            assert msg_id not in remaining_ids

    def test_clear_inbox(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s, _ = self._setup(c)
            resp = c.delete(f"/agents/mgmt/messages?secret={s}")
            assert resp.get_json()["ok"] is True

            inbox = c.get(f"/agents/mgmt/messages?secret={s}").get_json()
            assert inbox["count"] == 0

    def test_sent_messages(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s, s2 = self._setup(c)
            sent = c.get(f"/agents/sender/messages/sent?secret={s2}").get_json()
            assert sent["ok"] is True
            assert sent["count"] >= 2


class TestDiscovery:
    def test_list_agents(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            c.post("/agents/register", json={"agent_id": "a1", "description": "first"})
            c.post("/agents/register", json={"agent_id": "a2", "description": "second"})
            resp = c.get("/agents")
            data = resp.get_json()
            assert data["count"] == 2
            ids = [a["agent_id"] for a in data["agents"]]
            assert "a1" in ids
            assert "a2" in ids

    def test_get_agent(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            c.post("/agents/register", json={
                "agent_id": "detailed",
                "description": "A detailed agent",
                "capabilities": ["research"]
            })
            resp = c.get("/agents/detailed")
            data = resp.get_json()
            assert data["agent_id"] == "detailed"
            assert data["description"] == "A detailed agent"
            assert "research" in data["capabilities"]
            assert "liveness" in data

    def test_get_nonexistent_agent(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            resp = c.get("/agents/nobody")
            assert resp.status_code == 404

    def test_match_agents(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            c.post("/agents/register", json={
                "agent_id": "security-bot",
                "description": "security audit specialist",
                "capabilities": ["security-audit", "code-review"]
            })
            c.post("/agents/register", json={
                "agent_id": "writer-bot",
                "description": "content writing",
                "capabilities": ["writing", "editing"]
            })
            resp = c.get("/agents/match?need=security")
            data = resp.get_json()
            assert len(data["matches"]) >= 1
            assert data["matches"][0]["agent_id"] == "security-bot"

    def test_list_discovered_empty(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            resp = c.get("/discover")
            data = resp.get_json()
            assert data["count"] == 0


class TestBroadcast:
    def test_broadcast(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            s1 = c.post("/agents/register", json={"agent_id": "broadcaster"}).get_json()["secret"]
            s2 = c.post("/agents/register", json={"agent_id": "listener1"}).get_json()["secret"]
            s3 = c.post("/agents/register", json={"agent_id": "listener2"}).get_json()["secret"]

            resp = c.post("/broadcast", json={
                "from": "broadcaster",
                "secret": s1,
                "payload": {"text": "announcement"}
            })
            data = resp.get_json()
            assert data["ok"] is True
            assert data["count"] == 2
            assert set(data["delivered_to"]) == {"listener1", "listener2"}

            # Check listener1 got it
            inbox = c.get(f"/agents/listener1/messages?secret={s2}").get_json()
            broadcast_msgs = [m for m in inbox["messages"] if m.get("is_broadcast")]
            assert len(broadcast_msgs) == 1


class TestLiveness:
    def test_liveness_in_agent_listing(self, msg_app):
        app, _ = msg_app
        with app.test_client() as c:
            c.post("/agents/register", json={"agent_id": "live-agent"})
            resp = c.get("/agents")
            agent = [a for a in resp.get_json()["agents"] if a["agent_id"] == "live-agent"][0]
            assert "liveness" in agent
            assert "liveness_class" in agent["liveness"]
            assert "delivery_capability" in agent["liveness"]


class TestEventHookIntegration:
    def test_on_agent_event_fires_on_poll(self, msg_app):
        app, _ = msg_app
        from hub.messaging import on_agent_event
        events = []
        on_agent_event.subscribe(lambda aid, etype, meta: events.append(etype))

        with app.test_client() as c:
            s = c.post("/agents/register", json={"agent_id": "poller"}).get_json()["secret"]
            c.get(f"/agents/poller/messages?secret={s}")

        assert "inbox_poll" in events

    def test_hooks_isolated_between_tests(self, msg_app):
        """Verify fixture clears hooks between tests."""
        from hub.messaging import on_message_sent
        assert len(on_message_sent) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
