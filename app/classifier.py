import io

import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps, UnidentifiedImageError
from tensorflow import keras

IMG_SIZE = (224, 224)


class Classifier:
    """Reconstruye el modelo del notebook, carga los pesos y devuelve el Top-3."""

    def __init__(self, weights_path: str, class_names_path: str):
        with open(class_names_path, encoding="utf-8") as f:
            self.class_names = [line.strip() for line in f if line.strip()]
        if len(self.class_names) != 101:
            raise ValueError(
                f"Se esperaban 101 clases y hay {len(self.class_names)}.")
        self.model = self._build_model()
        self.model.load_weights(weights_path)

    @staticmethod
    def _build_model() -> keras.Model:
        # Misma arquitectura que la celda 3.1 del notebook.
        base = keras.applications.MobileNetV3Large(
            input_shape=(224, 224, 3), include_top=False, weights=None)
        base.trainable = False
        inputs = keras.Input(shape=(224, 224, 3))
        x = base(inputs, training=False)
        x = keras.layers.GlobalAveragePooling2D()(x)
        x = keras.layers.Dropout(0.2)(x)
        outputs = keras.layers.Dense(101, activation="softmax")(x)
        return keras.Model(inputs, outputs)

    @staticmethod
    def preprocess(image_bytes: bytes) -> np.ndarray:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
        except (UnidentifiedImageError, OSError):
            raise ValueError("No se pudo leer la imagen.")
        arr = np.array(img)                      # uint8, (alto, ancho, 3)
        arr = tf.image.resize(arr, IMG_SIZE)     # float32, 0-255, como en el entrenamiento
        return arr.numpy()[np.newaxis]           # (1, 224, 224, 3)

    def predict(self, image_bytes: bytes, k: int = 3) -> list[dict]:
        x = self.preprocess(image_bytes)
        p = self.model(x, training=False).numpy()[0]
        top = p.argsort()[::-1][:k]
        return [{"class_name": self.class_names[i], "confidence": float(p[i])}
                for i in top]
