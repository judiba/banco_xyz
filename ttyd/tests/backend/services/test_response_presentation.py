from backend.services.response_presentation import (
    can_view_raw_metrics,
    present_assistant_response,
)


def test_admin_sees_raw_values():
    text = "Share médio: 23.5 e crescimento 0.08"
    assert present_assistant_response(text, ["ttyd:admin"]) == text


def test_user_sees_percent_masked():
    text = "Share médio: 23.5 e crescimento 0.08"
    out = present_assistant_response(text, ["ttyd:user"])
    assert "23,5%" in out
    assert "8%" in out
    assert "23.5" not in out


def test_time_not_masked():
    text = "Pico entre 21:15 e 21:45"
    out = present_assistant_response(text, ["ttyd:user"])
    assert "21:15" in out
    assert "21:45" in out


def test_can_view_raw_metrics():
    assert can_view_raw_metrics(["ttyd:user"]) is False
    assert can_view_raw_metrics(["ttyd:admin"]) is True
    assert can_view_raw_metrics(["custom-admin-role"]) is True
