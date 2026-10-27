"""Interface checks: every page renders without error and the main flows work.
Run:  python -m pytest test_app.py
"""

import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["views/home.py", "views/find.py", "views/dashboard.py", "views/calibration.py",
         "views/data.py", "views/about.py"]


def start() -> AppTest:
    at = AppTest.from_file("app.py", default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    return at


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page):
    at = start()
    at.switch_page(page).run()
    assert not at.exception, at.exception
    assert not at.error


def test_home_shows_team_figures():
    at = start()
    values = {m.label: m.value for m in at.metric}
    assert values["Commuters"] == "200"
    assert values["Groups formed"] == "20"   # demo dataset, default rules (see README)


def test_find_my_group_default_trip_finds_a_group():
    at = start()
    at.switch_page("views/find.py").run()
    html = " ".join(m.value for m in at.markdown)
    assert "Group found" in html


def test_add_me_to_pool_updates_counts():
    at = start()
    at.switch_page("views/find.py").run()
    next(b for b in at.button if "Add me" in b.label).click().run()
    assert not at.exception, at.exception
    assert len(at.session_state["added"]) == 1
    at.switch_page("views/dashboard.py").run()
    assert {m.label: m.value for m in at.metric}["Commuters"] == "201"


def test_rules_change_updates_dashboard():
    at = start()
    at.switch_page("views/dashboard.py").run()
    before = {m.label: m.value for m in at.metric}["Groups formed"]
    at.slider(key="max_d").set_value(7.5).run()
    after = {m.label: m.value for m in at.metric}["Groups formed"]
    assert int(after) > int(before)


def test_original_dataset_without_gender_columns():
    at = start()
    at.radio(key="dataset").set_value("Train night (team's original file)").run()
    assert not at.exception, at.exception
    assert {m.label: m.value for m in at.metric}["Groups formed"] == "23"
