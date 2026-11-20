import pandas as pd


class NutritionTable:
    """Carga data/nutrition.csv una vez y estima kcal y macros según gramos."""

    COLUMNS = ["class_name", "standard_grams", "kcal",
               "protein_g", "carbs_g", "fat_g", "usda_source"]

    def __init__(self, csv_path: str):
        df = pd.read_csv(csv_path)
        missing = set(self.COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Faltan columnas en el CSV: {sorted(missing)}")
        self._df = df.set_index("class_name")

    def has(self, class_name: str) -> bool:
        return class_name in self._df.index

    def estimate(self, class_name: str, grams: float | None = None) -> dict:
        if not self.has(class_name):
            raise KeyError(f"Clase no encontrada: {class_name}")
        row = self._df.loc[class_name]
        standard = float(row["standard_grams"])
        used = standard if grams is None else float(grams)
        if used <= 0:
            raise ValueError("Los gramos deben ser mayores que 0.")
        factor = used / standard
        return {
            "class_name": class_name,
            "grams": round(used, 1),
            "standard_grams": round(standard, 1),
            "kcal": round(float(row["kcal"]) * factor),
            "protein_g": round(float(row["protein_g"]) * factor, 1),
            "carbs_g": round(float(row["carbs_g"]) * factor, 1),
            "fat_g": round(float(row["fat_g"]) * factor, 1),
        }
