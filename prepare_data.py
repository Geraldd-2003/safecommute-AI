"""
Builds the demo datasets used by the app from the team's train_data.xlsx.

1. data/train_data.xlsx       - the team's original file (input, unchanged).
2. data/train_data_demo.xlsx  - same 200 rows + two SIMULATED columns:
     Gender      : guessed from the first name (all first names in the file
                   are common French names), for demo purposes only.
     Women_Only  : about 35% of women tick "women-only" (random, fixed seed).
   In the real app both would be declared by each user at sign-up.
3. data/test_data.xlsx        - 200 new commuters for another night
   (17-18 Nov 2026), drawn from the same places and the same distributions
   as the train file, with the Gender / Women_Only columns.

Run:  python prepare_data.py
"""

import random
from pathlib import Path

import pandas as pd

OUT = Path(__file__).parent / "data"
SRC = OUT / "train_data.xlsx"   # the team's original file, never modified

FEMALE = {"Alice", "Camille", "Charlotte", "Chloe", "Chloé", "Clara", "Emma", "Inès", "Jade",
          "Louise", "Léa", "Manon", "Marie", "Noémie", "Sarah", "Sophie", "Lina", "Zoé"}
MALE = {"Adam", "Alexandre", "Antoine", "Arthur", "Gabriel", "Hugo", "Jules", "Julien", "Louis",
        "Lucas", "Léo", "Maxime", "Nicolas", "Paul", "Thomas", "Raphaël", "Nathan"}
WOMEN_ONLY_SHARE = 0.35


def gender_from_name(name: str) -> str:
    first = str(name).split()[0]
    return "F" if first in FEMALE else "M" if first in MALE else "Not declared"


def add_demo_profile(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    df = df.copy()
    df["Gender"] = df["User_Name"].map(gender_from_name)
    df["Women_Only"] = [g == "F" and rng.random() < WOMEN_ONLY_SHARE for g in df["Gender"]]
    return df


def make_test_set(train: pd.DataFrame, seed: int, n: int = 200) -> pd.DataFrame:
    """New commuters sampled from the train file's places, slots and modes."""
    rng = random.Random(seed)
    origins = train.groupby("Origin_Address")[["Origin_Lat", "Origin_Lng"]].mean()
    dests = train.groupby("Destination_Address")[["Destination_Lat", "Destination_Lng"]].mean()
    o_w = train["Origin_Address"].value_counts()
    d_w = train["Destination_Address"].value_counts()
    t_w = train["Transport_Preference"].value_counts()
    s_w = train["Travel_Time_Slot"].value_counts()
    o_sd = train.groupby("Origin_Address")["Origin_Lat"].std().mean()
    d_sd = train.groupby("Destination_Address")["Destination_Lat"].std().mean()

    first_f, first_m = sorted(FEMALE - {"Chloé", "Lina", "Zoé"}), sorted(MALE - {"Raphaël", "Nathan"})
    lasts = sorted({str(x).split()[-1] for x in train["User_Name"]})

    def shift_slot(slot):  # same night pattern, one week later
        date, rest = slot.split(" ", 1)
        return (pd.Timestamp(date) + pd.Timedelta(days=7)).strftime("%Y-%m-%d") + " " + rest

    rows = []
    for i in range(1, n + 1):
        o = rng.choices(list(o_w.index), list(o_w.values))[0]
        d = rng.choices(list(d_w.index), list(d_w.values))[0]
        female = rng.random() < 0.5
        rows.append({
            "User_ID": f"TST-{i:04d}",
            "User_Name": f"{rng.choice(first_f if female else first_m)} {rng.choice(lasts)}",
            "Origin_Address": o,
            "Origin_Lat": round(origins.loc[o, "Origin_Lat"] + rng.gauss(0, o_sd), 6),
            "Origin_Lng": round(origins.loc[o, "Origin_Lng"] + rng.gauss(0, o_sd), 6),
            "Destination_Address": d,
            "Destination_Lat": round(dests.loc[d, "Destination_Lat"] + rng.gauss(0, d_sd), 6),
            "Destination_Lng": round(dests.loc[d, "Destination_Lng"] + rng.gauss(0, d_sd), 6),
            "Transport_Preference": rng.choices(list(t_w.index), list(t_w.values))[0],
            "Travel_Time_Slot": shift_slot(rng.choices(list(s_w.index), list(s_w.values))[0]),
        })
    return add_demo_profile(pd.DataFrame(rows), seed + 1)


def save(df: pd.DataFrame, path: Path) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        df.to_excel(xw, index=False, sheet_name="Sheet1")
        ws = xw.sheets["Sheet1"]
        for col in ws.columns:
            w = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(w + 2, 55)
        ws.freeze_panes = "A2"


if __name__ == "__main__":
    train = pd.read_excel(SRC)
    demo = add_demo_profile(train, seed=42)
    save(demo, OUT / "train_data_demo.xlsx")
    test = make_test_set(train, seed=2026)
    save(test, OUT / "test_data.xlsx")
    for name, df in [("train_demo", demo), ("test", test)]:
        print(f"{name}: {len(df)} rows | women {(df.Gender == 'F').sum()} | "
              f"women-only {df.Women_Only.sum()} | undeclared {(df.Gender == 'Not declared').sum()}")
