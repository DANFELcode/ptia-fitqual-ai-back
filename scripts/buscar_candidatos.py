import sys
from pathlib import Path

import pandas as pd

USDA = Path("../usda/FoodData_Central_survey_food_csv_2024-10-31")
food = pd.read_csv(USDA / "food.csv", usecols=["fdc_id", "description"])
food["lower"] = food["description"].str.lower()
clases = Path("models/class_names.txt").read_text(encoding="utf-8").split()

desde = int(sys.argv[1]) if len(sys.argv) > 1 else 0
hasta = int(sys.argv[2]) if len(sys.argv) > 2 else len(clases)

for i in range(desde, hasta):
    nombre = clases[i]
    palabras = [p for p in nombre.split("_") if p != "and"]
    mask = pd.Series(True, index=food.index)
    for p in palabras:
        mask &= food["lower"].str.contains(p, regex=False)
    cand = food[mask].copy()
    cand["largo"] = cand["description"].str.len()
    cand = cand.sort_values("largo").head(3)
    print(f"{i} {nombre}")
    if cand.empty:
        print("   (sin coincidencias)")
    for _, r in cand.iterrows():
        print(f"   {r.fdc_id}  {r.description}")
