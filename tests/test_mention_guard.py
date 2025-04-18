import pytest
from bot.mention_guard import MentionGuard
import time

@pytest.fixture
def guard():
    guard = MentionGuard()
    guard.general_roasts = ["طقطقة 1", "طقطقة 2"]
    return guard

def test_special_response(guard):
    guard.add_special_responses("testuser", ["رد خاص 1", "رد خاص 2"])
    result = guard.handle_mention("testuser")
    assert result["action"] == "roast"
    assert result["message"] in ["رد خاص 1", "رد خاص 2"]

def test_warning_then_timeout(guard):
    guard.set_config(limit=3, duration=5, cooldown=86400, warning_thresh=2, warn_msg="تحذير!", timeout_msg="تايم أوت!")
    assert guard.handle_mention("normaluser")["action"] == "roast"
    assert guard.handle_mention("normaluser")["action"] == "warn"
    timeout_result = guard.handle_mention("normaluser")
    assert timeout_result["action"] == "timeout"
    assert timeout_result["duration"] == 5

def test_cooldown_after_timeout(guard):
    guard.no_timeout_users["cooluser"] = time.time()
    result = guard.handle_mention("cooluser")
    assert result["action"] == "roast"
