# FitQual AI - Backend

Backend del proyecto **FitQual AI** (estimación de calorías a partir de una foto de comida) de la materia Principios y Tecnologías de IA (PTIA), Escuela Colombiana de Ingeniería.

**Entrega final (Hito 3):** [Video de presentación y demo del MVP](https://youtu.be/YQqdyIhd7so) · [Notebook de entrenamiento y evaluación](notebooks/fitqual_entrenamiento_final.ipynb)

Recibe una foto, reconoce el plato entre 101 categorías (Food-101) y calcula calorías, proteína, carbohidratos y grasa a partir de una tabla USDA.

- Frontend (React + Vite): https://github.com/JUDAMUCH03/ptia-fitqual-ai-front

## Cómo correrlo (Docker)

```bash
docker build -t fitqual-back .
docker run --rm -p 8001:8000 fitqual-back
```

El servicio queda en http://127.0.0.1:8001. Para comprobar que funciona:

```bash
curl http://127.0.0.1:8001/health
```

## Variables de entorno

| Variable | Qué hace | Valor por defecto |
|---|---|---|
| `ALLOWED_ORIGINS` | Direcciones del front que pueden llamar al back (CORS). No se permite `*`. | `http://localhost:5173` y `http://127.0.0.1:5173` |

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/health` | Indica si el servicio está vivo. |
| POST | `/api/predict` | Recibe una foto (multipart, campo `file`). Devuelve las 3 clases más probables con su confianza, `confident` (true si la primera tiene 0,70 o más) y `threshold` (0,7). |
| POST | `/api/estimate` | Recibe JSON `{class_name, grams}` (`grams` puede ser `null` para usar la porción estándar). Devuelve gramos, porción estándar, kcal, proteína, carbohidratos y grasa. |

Los errores (400 y 404) devuelven `{"detail": "mensaje en español"}`.

## Modelo

MobileNetV3Large con transfer learning sobre Food-101 (101 clases). Resultado en el test: Top-1 69,7 % y Top-5 90,7 %. El objetivo del Hito 2 era superar 70 % en Top-1: no se cumplió por 0,3 puntos. Los pesos están en `models/fitqual.weights.h5` y los nombres de las clases en `models/class_names.txt`.

## Datos nutricionales

`data/nutrition.csv` tiene una fila por clase. Fuente: USDA FoodData Central (FNDDS). Se generó con los scripts de `scripts/`, usando el mapeo de `scripts/mapeo.csv`.

- Los archivos originales de USDA **no están en este repositorio** (se descargaron aparte, en la carpeta `../usda`).
- Los valores de USDA se tomaron como "por 100 g" (convención de USDA, **sin verificar** contra su documentación de campos).
- Unas 30 de las 101 clases son aproximaciones (por ejemplo, `escargots` usa almejas, `fish_and_chips` usa solo pescado). La lista está en `scripts/mapeo.csv`.

## Limitaciones

- La app no mide cuánta comida hay en la foto: el usuario indica los gramos. Si no los ajusta, usa la porción estándar y puede subestimar.
- Solo reconoce las 101 categorías de Food-101 (no reconoce, por ejemplo, una arepa).
- Es una estimación basada en porciones estándar de USDA; no reemplaza asesoría nutricional.
