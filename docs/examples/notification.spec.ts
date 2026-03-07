// Notification fixture tests for spam/noise regression prevention.
// References:
// - ../notification-transition-matrix-v0.1.md
// - ./review-state.ts

import {
  type Blocker,
  type NotificationDecision,
  type ReviewStatePacket,
  buildNotificationTuple,
  notificationDecision,
  validateRiskPhaseInvariant,
} from "./review-state.ts";

interface NotificationFixture {
  name: string;
  previous: ReviewStatePacket;
  next: ReviewStatePacket;
  expected: {
    emit: boolean;
    reason: NotificationDecision["reason"];
    priority: NotificationDecision["priority"];
    tuple?: Partial<ReturnType<typeof buildNotificationTuple>>;
  };
}

interface RiskPhaseInvariantFixture {
  name: string;
  previous: ReviewStatePacket;
  next: ReviewStatePacket;
  expected: {
    valid: boolean;
    reason: "ok" | "risk-phase-improved-without-supporting-change";
  };
}

function blocker(id: string, type: Blocker["type"], summary: string): Blocker {
  return {
    id,
    type,
    summary,
    resolutionCondition: summary,
    evidenceIds: [id],
  };
}

function packet(overrides: Partial<ReviewStatePacket>): ReviewStatePacket {
  return {
    repo: "alexjaniak/DACL",
    prNumber: 99,
    prUrl: "https://github.com/alexjaniak/DACL/pull/99",
    state: "blocked",
    confidencePct: 95,
    headSha: "999zzzz",
    baseBranch: "main",
    evaluatedAt: "2026-03-07T06:50:00Z",
    profileId: "alexjaniak/DACL/review-v1",
    profileVersion: "1",
    blockers: [],
    actionLine: "To merge: reevaluate current head.",
    actionKey: "resolve.blockers.none",
    ...overrides,
  };
}

export const notificationFixtures: NotificationFixture[] = [
  {
    name: "action_line rewrite alone never emits",
    previous: packet({
      state: "blocked",
      blockers: [blocker("pending-required-check:check:dashboard-verify", "pending-required-check", "Wait for dashboard-verify")],
      actionLine: "Wait for dashboard-verify to finish.",
      actionKey: "wait.check.dashboard-verify",
      confidencePct: 95,
    }),
    next: packet({
      state: "blocked",
      blockers: [blocker("pending-required-check:check:dashboard-verify", "pending-required-check", "Wait for dashboard-verify")],
      actionLine: "Await CI completion (dashboard-verify).",
      actionKey: "wait.check.dashboard-verify",
      confidencePct: 95,
    }),
    expected: {
      emit: false,
      reason: "no-op",
      priority: "low",
      tuple: {
        blockerSetChanged: false,
        actionKeyChanged: false,
        mergeableFlip: "none",
      },
    },
  },
  {
    name: "threshold confidence drop always emits",
    previous: packet({
      state: "needs-human",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Reconfirm reviewer intent")],
      actionLine: "Do not merge because prior approval was for superseded SHA; reconfirm reviewer intent on current head.",
      actionKey: "reconfirm.intent.current-head",
      confidencePct: 72,
    }),
    next: packet({
      state: "needs-human",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Reconfirm reviewer intent")],
      actionLine: "Do not merge because prior approval was for superseded SHA; reconfirm reviewer intent on current head.",
      actionKey: "reconfirm.intent.current-head",
      confidencePct: 38,
    }),
    expected: {
      emit: true,
      reason: "confidence-drop",
      priority: "normal",
      tuple: {
        blockerSetChanged: false,
        actionKeyChanged: false,
        confidenceDropBucket: "threshold_cross",
      },
    },
  },
  {
    name: "risk phase escalation emits even with same blocker and action key",
    previous: packet({
      state: "needs-human",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Reconfirm reviewer intent")],
      actionLine: "Do not merge because current-head intent is ambiguous.",
      actionKey: "reconfirm.intent.current-head",
      riskPhase: "ambiguous",
      confidencePct: 74,
    }),
    next: packet({
      state: "needs-human",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Reconfirm reviewer intent")],
      actionLine: "Do not merge because current-head intent is ambiguous.",
      actionKey: "reconfirm.intent.current-head",
      riskPhase: "explicit-blocking",
      confidencePct: 58,
    }),
    expected: {
      emit: true,
      reason: "confidence-drop",
      priority: "high",
      tuple: {
        blockerSetChanged: false,
        actionKeyChanged: false,
        confidenceDropBucket: "severe",
      },
    },
  },
  {
    name: "severe confidence drop always emits",
    previous: packet({
      state: "blocked",
      blockers: [blocker("pending-required-check:check:solana-bootstrap-sdk", "pending-required-check", "Wait for solana-bootstrap-sdk")],
      actionLine: "To merge: wait for solana-bootstrap-sdk to finish.",
      actionKey: "wait.check.solana-bootstrap-sdk",
      confidencePct: 59,
    }),
    next: packet({
      state: "blocked",
      blockers: [blocker("pending-required-check:check:solana-bootstrap-sdk", "pending-required-check", "Wait for solana-bootstrap-sdk")],
      actionLine: "To merge: wait for solana-bootstrap-sdk to finish.",
      actionKey: "wait.check.solana-bootstrap-sdk",
      confidencePct: 20,
    }),
    expected: {
      emit: true,
      reason: "confidence-drop",
      priority: "high",
      tuple: {
        blockerSetChanged: false,
        actionKeyChanged: false,
        confidenceDropBucket: "severe",
      },
    },
  },
  {
    name: "same blocker ids but changed action_key emits",
    previous: packet({
      state: "blocked",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Human review needed")],
      actionLine: "Ask alexjaniak to reaffirm resolution on current head.",
      actionKey: "reconfirm.intent.thread-901.head.333cccc",
      confidencePct: 78,
    }),
    next: packet({
      state: "blocked",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Human review needed")],
      actionLine: "Obtain approval from alexjaniak on current head.",
      actionKey: "need.approval.alexjaniak",
      confidencePct: 78,
    }),
    expected: {
      emit: true,
      reason: "action-line-change",
      priority: "normal",
      tuple: {
        blockerSetChanged: false,
        actionKeyChanged: true,
      },
    },
  },
  {
    name: "pending-age churn never emits",
    previous: packet({
      state: "blocked",
      blockers: [blocker("pending-required-check:check:solana-bootstrap-sdk", "pending-required-check", "Wait for solana-bootstrap-sdk")],
      actionLine: "To merge: wait for solana-bootstrap-sdk to finish on head 333cccc.",
      actionKey: "wait.check.solana-bootstrap-sdk",
      confidencePct: 96,
    }),
    next: packet({
      state: "blocked",
      blockers: [blocker("pending-required-check:check:solana-bootstrap-sdk", "pending-required-check", "Wait for solana-bootstrap-sdk")],
      actionLine: "To merge: wait for solana-bootstrap-sdk to finish on head 333cccc.",
      actionKey: "wait.check.solana-bootstrap-sdk",
      confidencePct: 96,
    }),
    expected: {
      emit: false,
      reason: "no-op",
      priority: "low",
      tuple: {
        blockerSetChanged: false,
        actionKeyChanged: false,
        confidenceDropBucket: "none",
      },
    },
  },
];

export const riskPhaseInvariantFixtures: RiskPhaseInvariantFixture[] = [
  {
    name: "riskPhase may not improve without supporting evidence change",
    previous: packet({
      state: "needs-human",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Reconfirm reviewer intent")],
      actionLine: "Do not merge because current-head intent is ambiguous.",
      actionKey: "reconfirm.intent.current-head",
      riskPhase: "explicit-blocking",
      confidencePct: 58,
    }),
    next: packet({
      state: "needs-human",
      blockers: [blocker("ambiguous-state:thread:901", "ambiguous-state", "Reconfirm reviewer intent")],
      actionLine: "Do not merge because current-head intent is ambiguous.",
      actionKey: "reconfirm.intent.current-head",
      riskPhase: "ambiguous",
      confidencePct: 82,
    }),
    expected: {
      valid: false,
      reason: "risk-phase-improved-without-supporting-change",
    },
  },
];

export function runNotificationFixtures() {
  return notificationFixtures.map((fixture) => {
    const tuple = buildNotificationTuple(fixture.previous, fixture.next);
    const decision = notificationDecision(tuple);
    const diffs: string[] = [];

    if (decision.emit !== fixture.expected.emit) {
      diffs.push(`emit mismatch: expected=${fixture.expected.emit} actual=${decision.emit}`);
    }

    if (decision.reason !== fixture.expected.reason) {
      diffs.push(`reason mismatch: expected=${fixture.expected.reason} actual=${decision.reason}`);
    }

    if (decision.priority !== fixture.expected.priority) {
      diffs.push(`priority mismatch: expected=${fixture.expected.priority} actual=${decision.priority}`);
    }

    for (const [key, expectedValue] of Object.entries(fixture.expected.tuple ?? {})) {
      const actualValue = (tuple as Record<string, unknown>)[key];
      if (actualValue !== expectedValue) {
        diffs.push(`tuple.${key} mismatch: expected=${String(expectedValue)} actual=${String(actualValue)}`);
      }
    }

    return {
      name: fixture.name,
      pass: diffs.length === 0,
      diffs,
      tuple,
      decision,
    };
  });
}

export function runRiskPhaseInvariantFixtures() {
  return riskPhaseInvariantFixtures.map((fixture) => {
    const result = validateRiskPhaseInvariant(fixture.previous, fixture.next);
    const diffs: string[] = [];

    if (result.valid !== fixture.expected.valid) {
      diffs.push(`valid mismatch: expected=${fixture.expected.valid} actual=${result.valid}`);
    }

    if (result.reason !== fixture.expected.reason) {
      diffs.push(`reason mismatch: expected=${fixture.expected.reason} actual=${result.reason}`);
    }

    return {
      name: fixture.name,
      pass: diffs.length === 0,
      diffs,
      result,
    };
  });
}

// Optional tiny runner when executed directly under a TS-aware runtime.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const maybeProcess = globalThis as any;
if (typeof maybeProcess?.argv !== "undefined" && maybeProcess.argv[1]?.endsWith("notification.spec.ts")) {
  const results = [...runNotificationFixtures(), ...runRiskPhaseInvariantFixtures()];
  for (const result of results) {
    const mark = result.pass ? "PASS" : "FAIL";
    // eslint-disable-next-line no-console
    console.log(mark, result.name, result.diffs);
  }
}
