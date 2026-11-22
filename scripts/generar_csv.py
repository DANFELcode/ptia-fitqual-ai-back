import csv, os, sys
d = "../usda/FoodData_Central_survey_food_csv_2024-10-31"
NUT = {"208": "kcal", "203": "protein_g", "204": "fat_g", "205": "carbs_g"}
mapeo = list(csv.DictReader(open("scripts/mapeo.csv", encoding="utf-8")))
need = {r["fdc_id"] for r in mapeo}
desc = {}
with open(os.path.join(d, "food.csv"), newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["fdc_id"] in need:
            desc[r["fdc_id"]] = r["description"]
vals = {}
with open(os.path.join(d, "food_nutrient.csv"), newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["fdc_id"] in need and r["nutrient_id"] in NUT:
            vals.setdefault(r["fdc_id"], {})[NUT[r["nutrient_id"]]] = float(r["amount"])
names = [l.strip() for l in open("models/class_names.txt", encoding="utf-8") if l.strip()]
mapped = [r["class_name"] for r in mapeo]
print("filas:", len(mapeo), "| faltan:", sorted(set(names) - set(mapped)), "| sobran:", sorted(set(mapped) - set(names)))
errores = [r["class_name"] for r in mapeo if len(vals.get(r["fdc_id"], {})) < 4]
if errores:
    print("SIN NUTRIENTES:", errores)
    sys.exit(1)
os.makedirs("data", exist_ok=True)
with open("data/nutrition.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["class_name", "standard_grams", "kcal", "protein_g", "carbs_g", "fat_g", "usda_source"])
    for r in mapeo:
        g = float(r["standard_grams"])
        v = vals[r["fdc_id"]]
        w.writerow([r["class_name"], g, round(v["kcal"] * g / 100, 1), round(v["protein_g"] * g / 100, 2),
                    round(v["carbs_g"] * g / 100, 2), round(v["fat_g"] * g / 100, 2),
                    "USDA FNDDS fdc_id " + r["fdc_id"] + ": " + desc[r["fdc_id"]]])
print("data/nutrition.csv escrito")
