# SafeCommute AI · User guide

This guide takes you from an empty computer to a working demo in about 10 minutes. No coding is needed.

---

## 1. Install and start

### 1.1 Install Python (once)
1. Go to https://www.python.org/downloads/ and install **Python 3.11 or newer**.
2. **Windows**: on the first installer screen, tick **"Add Python to PATH"**, then click *Install Now*.
3. Check it worked: open a terminal (Windows: *Command Prompt*; Mac: *Terminal*) and type `python --version` (Mac: `python3 --version`). You should see `Python 3.11` or higher.

### 1.2 Start the app
1. Unzip the project folder `safecommute_app` anywhere (e.g. your Desktop).
2. Start it:
   - **Windows**: double-click **`run_app.bat`**.
   - **Mac / Linux**: open Terminal, type `cd ` (with a space), drag the folder into the window, press Enter, then type `bash run_app.sh` and press Enter.
3. The first start installs the packages (1–2 minutes). Your browser then opens **http://localhost:8501** with the app.
4. To stop the app, close the terminal window (or press `Ctrl + C` in it).

> Internet is needed for the map background (OpenStreetMap) and the address search. Without internet, the app still works: the map shows points on a grey background and you pick places from the lists.

---

## 2. The screen

- **Left sidebar**: the dataset and the matching rules. Changing anything here updates every tab instantly.
- **Tabs at the top**: 🗺️ Find my group · 📊 Dashboard · 🎯 Calibration · 📁 Data · ℹ️ About.

### Sidebar settings

| Setting | Default | What it changes |
|---|---|---|
| Dataset | Team train data + simulated gender | Which commuters are in the pool. *Upload my own file* accepts an Excel/CSV with the same columns (see §6). |
| Max distance between starting points | 1.0 km | How far apart two people can start and still travel together. |
| Max distance between destinations | 3.0 km | How far apart group members' destinations can be. |
| Max group size | 4 | Largest group allowed. |
| Respect women-only preferences | On | When off, the women-only ticks are ignored (useful to measure their cost). |

---

## 3. 🗺️ Find my group (commuter view)

You play a commuter who just got off the train.

1. **Where do you leave from?** Choose one of three ways:
   - pick a station or campus in the list, or
   - type an address in the search box and click 🔍 (needs internet), or
   - on the map, keep **🟢 Start** selected above the map and click where you are.
   The green box shows your current start.
2. **Where are you going?** Same three ways. To use the map, first select **🔴 Destination** above the map, then click.
3. **When, and who are you?** Choose your departure time slot, your name, your gender (optional) and the transport you take after.
   If you chose *Woman*, you can tick **"I only want to travel with women"**.

The result appears **immediately below**, and the map updates:

- ✅ **Green card**: you are in a group. You see the other members (first name + initial only), the meeting point, your walk to it and how far the furthest member's destination is from yours.
- ❌ **Red card**: no group yet. The card says why (e.g. *"3 people leave nearby, but none heads within 3 km of your destination"*), and a table lists the time slots where you **would** have company.

On the map:

| Symbol | Meaning |
|---|---|
| Green pin (walking person) | Your start |
| Red pin (house) | Your destination |
| Purple pin (people) | Group meeting point |
| Blue dots / rings | Other group members' starts / destinations |
| Dashed lines | From the meeting point to each member's destination |
| Grey dots | Other commuters leaving in the same slot (not in your group) |

4. Click **➕ Add me to the pool** to become visible to others. The Dashboard then counts you (201 commuters instead of 200). *Remove them* in the sidebar takes you out again.

---

## 4. 📊 Dashboard (operator view)

1. The five figures at the top: commuters, groups formed, matched (and %), people travelling alone, women-only users matched.
2. The bar chart shows, for each half-hour slot, how many people were matched (green) or left alone (grey).
3. Choose a **time slot** under the chart to see all its groups on the map, each in its own colour. Hover over a dot or pin to see who and where.
4. **Groups** table: one row per member, with the meeting point and walking distance.
5. **Why people were not matched**: reasons grouped and counted; open the expander to see every unmatched person and their reason.
6. **⬇️ Download all results (Excel)**: a workbook with Summary, By_Time_Slot, Groups and Unmatched sheets.

---

## 5. 🎯 Calibration (how the limits were chosen)

The two distance limits are the "settings" of our AI. We choose them on the **train** night and check them on the **test** night.

- **Left heatmap, coverage**: share of commuters matched for each pair of limits. Greener = more people matched.
- **Right heatmap, destination spread**: average largest distance between two members' destinations. Darker = the last person walks alone for longer.
- **Table**: the current sidebar limits applied to train and to test. A small gap between the two means the rules work on a night they were not chosen on.

Try moving the sidebar sliders and watch the table change.

---

## 6. 📁 Data, and using your own file

The Data tab shows the active dataset, its size and the busiest start points and destinations.

To use your own data: choose **Upload my own file** in the sidebar and drop an `.xlsx` or `.csv` with these columns:

| Column | Example |
|---|---|
| User_ID | USR-0001 (must be unique) |
| User_Name | Inès Girard |
| Origin_Address | Gare de Cergy-Préfecture, 95000 Cergy |
| Origin_Lat, Origin_Lng | 49.0367, 2.0794 |
| Destination_Address | Osny Gare, 95520 Osny |
| Destination_Lat, Destination_Lng | 49.0621, 2.0595 |
| Transport_Preference | RER, Bus, Metro… |
| Travel_Time_Slot | 2026-11-10 22:30 - 23:00 |
| Gender *(optional)* | F or M |
| Women_Only *(optional)* | True or False |

If a column is missing or a coordinate is not a number, the app says which one.

---

## 7. Suggested demo path (≈ 2 minutes of the video)

1. **Find my group**, default trip: ESSEC → Éragny-sur-Oise, 22:00–22:30 → *"You're travelling with 2 people"*, meeting point at the ESSEC exit.
2. Select **🔴 Destination** and click somewhere else on the map → the group changes live.
3. Gender *Woman* + tick *women-only* → the group now contains only women.
4. Untick women-only, set gender back to *Prefer not to say*, pick *Versailles Château Rive Gauche* as destination and the **21:30–22:00** slot → red card: *"7 people leave nearby, but none heads within 3 km of the destination"*, plus the slots where you would have company (e.g. 22:30–23:00 with 2 people).
5. **Dashboard** → busiest slot on the map, reasons for non-matches, Excel export.
6. **Calibration** → the coverage vs. safety trade-off and train vs. test.

---

## 8. Re-running everything from scratch (reproducibility)

In a terminal opened in the project folder:

```
pip install -r requirements.txt
python test_engine.py                  # expected: 10 tests passed
python prepare_data.py                 # rebuilds data/train_data_demo.xlsx and data/test_data.xlsx
python engine.py data/train_data.xlsx  # expected: 23 groups, 52 / 200 matched (26.0%)
streamlit run app.py
```

The random parts (simulated gender, test night) use fixed seeds, so everyone gets the same files and figures.

---

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognised (Windows) | Reinstall Python and tick "Add Python to PATH", or use `py` instead of `python`. |
| Map is grey with only dots | No internet access to OpenStreetMap; the app still works. |
| "Address search needs an internet connection" | Same cause; pick from the list or click on the map. |
| "No address found" | Add the town name, e.g. "Gare de Pontoise, Pontoise". |
| Port 8501 already in use | Close the other app window, or run `streamlit run app.py --server.port 8502`. |
| Error when uploading a file | The message names the missing column or the bad value; fix it in Excel and upload again. |
| Install fails on an old Python | Python 3.11 or newer is required. |
