class UncertaintyGate:
    """Decide si la predicción es confiable según el umbral θ."""

    def __init__(self, threshold: float = 0.70):
        if not 0.0 < threshold <= 1.0:
            raise ValueError("El umbral debe estar entre 0 y 1.")
        self.threshold = threshold

    def evaluate(self, top3: list[dict]) -> dict:
        if not top3:
            raise ValueError("La lista de predicciones está vacía.")
        return {
            "top3": top3,
            "confident": top3[0]["confidence"] >= self.threshold,
            "threshold": self.threshold,
        }
