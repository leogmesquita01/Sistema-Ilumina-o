from app.dashboard.html_seguro import esc


def test_esc():
    assert esc('<img src=x onerror="alert(1)">') == "&lt;img src=x onerror=&quot;alert(1)&quot;&gt;"
    assert esc(None) == "—"
    assert esc("  ", "") == ""
    assert esc(100) == "100"
