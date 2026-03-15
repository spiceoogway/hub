#!/usr/bin/env python3
"""
Colony comment deduplication helper.
Before posting a comment, check if brain-agent already replied 
to the same post after a given timestamp.

Usage:
    from colony_dedup import should_reply
    if should_reply(post_id, after_timestamp):
        # post the comment
    else:
        # skip, already replied
"""

import requests
import json
import os
from datetime import datetime

def get_colony_jwt():
    """Get Colony JWT from credentials."""
    jwt_path = os.path.expanduser('~/.openclaw/workspace/credentials/colony_jwt.txt')
    if os.path.exists(jwt_path):
        return open(jwt_path).read().strip()
    return None

def should_reply(post_id: str, after_comment_id: str = None, after_timestamp: str = None) -> bool:
    """
    Check if brain-agent should reply to a Colony post.
    Returns False if brain-agent already commented after the given comment/timestamp.
    
    Args:
        post_id: Colony post ID
        after_comment_id: If set, check if brain-agent commented after this comment
        after_timestamp: If set, check if brain-agent commented after this ISO timestamp
    """
    jwt = get_colony_jwt()
    if not jwt:
        return True  # Can't check, allow reply
    
    headers = {'Authorization': f'Bearer {jwt}'}
    
    try:
        r = requests.get(
            f'https://thecolony.cc/api/v1/posts/{post_id}/comments',
            headers=headers,
            timeout=10
        )
        if r.status_code != 200:
            return True  # Can't check, allow reply
        
        comments = r.json() if isinstance(r.json(), list) else r.json().get('comments', [])
        
        # Find the target comment position
        target_idx = -1
        if after_comment_id:
            for i, c in enumerate(comments):
                if c.get('id', '').startswith(after_comment_id):
                    target_idx = i
                    break
        
        # Check if brain-agent already replied after target
        check_from = target_idx + 1 if target_idx >= 0 else 0
        
        for c in comments[check_from:]:
            author = c.get('author', {})
            if isinstance(author, dict):
                username = author.get('username', '')
            else:
                username = str(author)
            
            if username == 'brain-agent':
                # Already replied
                if after_timestamp:
                    comment_time = c.get('created_at', '')
                    if comment_time >= after_timestamp:
                        return False
                else:
                    return False
        
        return True  # No brain-agent reply found after target
        
    except Exception:
        return True  # Error, allow reply

def brain_last_comment_on(post_id: str) -> dict:
    """Get brain-agent's most recent comment on a post."""
    jwt = get_colony_jwt()
    if not jwt:
        return None
    
    headers = {'Authorization': f'Bearer {jwt}'}
    
    try:
        r = requests.get(
            f'https://thecolony.cc/api/v1/posts/{post_id}/comments',
            headers=headers,
            timeout=10
        )
        if r.status_code != 200:
            return None
        
        comments = r.json() if isinstance(r.json(), list) else r.json().get('comments', [])
        
        brain_comments = []
        for c in comments:
            author = c.get('author', {})
            username = author.get('username', '') if isinstance(author, dict) else str(author)
            if username == 'brain-agent':
                brain_comments.append(c)
        
        return brain_comments[-1] if brain_comments else None
        
    except Exception:
        return None


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python colony_dedup.py <post_id> [after_comment_id]")
        sys.exit(1)
    
    post_id = sys.argv[1]
    after_cid = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = should_reply(post_id, after_comment_id=after_cid)
    print(f"Should reply: {result}")
    
    last = brain_last_comment_on(post_id)
    if last:
        print(f"Last brain comment: {last.get('id','')[:12]} at {last.get('created_at','')[:19]}")
