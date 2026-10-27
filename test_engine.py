"""Checks of the matching rules on small hand-made cases.
Run:  python test_engine.py   (or: pytest test_engine.py)
"""

import pandas as pd

import engine as E

ESSEC = (49.0356, 2.0692)
OSNY = (49.0621, 2.0595)
VERSAILLES = (48.7991, 2.1287)
SLOT = "2026-11-10 22:00 - 22:30"


def user(uid, origin=ESSEC, dest=OSNY, slot=SLOT, gender="F", women_only=False, d_lat=0.0):
    return {"User_ID": uid, "User_Name": f"Test {uid}", "Origin_Address": "o",
            "Origin_Lat": origin[0], "Origin_Lng": origin[1], "Destination_Address": "d",
            "Destination_Lat": dest[0] + d_lat, "Destination_Lng": dest[1],
            "Transport_Preference": "Bus", "Travel_Time_Slot": slot,
            "Gender": gender, "Women_Only": women_only}


def frame(*users):
    return E.prepare_dataset(pd.DataFrame(users))


def test_two_close_people_match():
    r = E.run_matching(frame(user("A"), user("B")))
    assert len(r.groups) == 1 and r.n_matched == 2


def test_different_slots_never_match():
    r = E.run_matching(frame(user("A"), user("B", slot="2026-11-10 22:30 - 23:00")))
    assert r.n_matched == 0


def test_far_destinations_never_match():
    r = E.run_matching(frame(user("A"), user("B", dest=VERSAILLES)))
    assert r.n_matched == 0


def test_far_origins_never_match():
    r = E.run_matching(frame(user("A"), user("B", origin=(ESSEC[0] + 0.02, ESSEC[1]))))  # ~2.2 km
    assert r.n_matched == 0


def test_group_capped_at_four():
    r = E.run_matching(frame(*[user(str(i)) for i in range(6)]))
    assert sorted(len(g) for g in r.groups) == [2, 4]


def test_women_only_respected():
    r = E.run_matching(frame(user("W", women_only=True), user("M", gender="M")))
    assert r.n_matched == 0
    r = E.run_matching(frame(user("W", women_only=True), user("F2")))
    assert r.n_matched == 2


def test_women_only_rule_can_be_switched_off():
    r = E.run_matching(frame(user("W", women_only=True), user("M", gender="M")),
                       E.MatchConfig(women_only_rule=False))
    assert r.n_matched == 2


def test_undeclared_gender_not_in_women_only_group():
    r = E.run_matching(frame(user("W", women_only=True), user("X", gender="Not declared")))
    assert r.n_matched == 0


def test_closest_pair_is_grouped_first():
    # C is closer to B than A is; with max size 2, B must end up with C.
    a = user("A", origin=(ESSEC[0] + 0.006, ESSEC[1]))
    b = user("B")
    c = user("C", origin=(ESSEC[0] - 0.001, ESSEC[1]))
    r = E.run_matching(frame(a, b, c), E.MatchConfig(max_group_size=2))
    assert {m["User_ID"] for m in r.groups[0]} == {"B", "C"}


def test_team_dataset_groups_respect_all_rules():
    df = E.load_dataset("data/train_data_demo.xlsx")
    r = E.run_matching(df)            # run_matching re-verifies every group
    ids = [m["User_ID"] for g in r.groups for m in g]
    assert len(ids) == len(set(ids))  # nobody in two groups
    assert r.n_matched + len(r.unmatched) == len(df)


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed")
