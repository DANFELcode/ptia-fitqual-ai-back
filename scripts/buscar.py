import sys
from pathlib import Path

import pandas as pd

USDA = Path("../usda/FoodData_Central_survey_food_csv_2024-10-31")
food = pd.read_csv(USDA / "food.csv", usecols=["fdc_id", "description"])
food["lower"] = food["description"].str.lower()

for termino in sys.argv[1:]:
    mask = pd.Series(True, index=food.index)
    for p in termino.lower().split():
        mask &= food["lower"].str.contains(p, regex=False)
    cand = food[mask].copy()
    cand["largo"] = cand["description"].str.len()
    print(f"[{termino}]")
    if cand.empty:
        print("   (sin coincidencias)")
    for _, r in cand.sort_values("largo").head(6).iterrows():
        print(f"   {r.fdc_id}  {r.description}")
