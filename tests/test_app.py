import sys
import os
import copy

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


def setup_function():
    # keep original snapshot for tests that mutate state
    global _ORIG_ACTIVITIES
    _ORIG_ACTIVITIES = copy.deepcopy(activities)


def teardown_function():
    # restore original activities after each test
    activities.clear()
    activities.update(_ORIG_ACTIVITIES)


def test_root_redirects_to_index():
    r = client.get("/")
    # TestClient follows redirects by default; accept final 200 or redirect codes
    assert r.status_code in (200, 301, 302, 307, 308)
    if r.status_code == 200:
        # final URL after redirect should be the index page
        assert "/static/index.html" in getattr(r.url, "path", str(r.url))
    else:
        # RedirectResponse sets Location header
        assert "/static/index.html" in r.headers.get("location", "")


def test_get_activities_returns_dict():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    email = "tester@example.com"
    # signup
    r = client.post("/activities/Chess Club/signup", params={"email": email})
    assert r.status_code == 200
    assert email in activities["Chess Club"]["participants"]

    # unregister
    r2 = client.post("/activities/Chess Club/unregister", params={"email": email})
    assert r2.status_code == 200
    assert email not in activities["Chess Club"]["participants"]
