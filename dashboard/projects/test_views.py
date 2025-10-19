import pytest

from django.urls import reverse

def test_toggle_condition_url_patterns():
    assert reverse(
        "projects:action_toggle_condition",
        args=[1],
        query={"status": "DO", "target": "done"}
    ) == "/action_toggle_condition/1?status=DO&target=done"
