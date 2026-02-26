# Fashion Classifier (StyleMePal - TFM)

Sistema profesional de clasificación de imágenes de moda basado en Deep Learning con TensorFlow y transfer learning, entrenado en el dataset Polyvore (251k imágenes, 11 categorías).

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![TensorFlow](https://img.shields.io/badge/tensorflow-2.15.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## Características Principales

- **Modelo**: EfficientNetB0 con transfer learning
- **Precisión**: 94.65% (Top-1) / 99.18% (Top-3)
- **Dataset**: Polyvore Fashion (251,008 imágenes)
- **Categorías**: 11 clases (accessories, bags, tops, shoes, etc.)
- **Entrenamiento**: 2 fases (frozen + fine-tuning)
- **Soporte GPU**: Optimizado para NVIDIA CUDA en WSL2

---

## Estructura del Proyecto

```
.
├── src/
│   └── fashion_classifier/     # Paquete principal
│       ├── __init__.py
│       └── __main__.py          # Entry point: python -m fashion_classifier
├── data/
│   ├── raw/                     # Datos originales (no versionados)
│   ├── processed/               # Datos preprocesados
│   └── external/
│       └── test_images/         # 14 imágenes de prueba
├── models/
│   ├── fashion_classifier_efficientnetb0_polyvore.keras  # Modelo entrenado
│   └── label_encoder.pkl        # Mapeo de categorías
├── notebooks/
│   ├── 01_training_polyvore_efficientnet.ipynb   # Pipeline completo de entrenamiento
│   └── 02_inference_test.ipynb                    # Inferencia y visualización
├── scripts/                     # Scripts de utilidad
├── reports/
│   ├── figures/
│   │   ├── confusion_matrix_polyvore.png
│   │   ├── training_history_polyvore.png
│   │   └── predictions_visualization_polyvore.png
│   └── model_metrics_polyvore.json
├── tests/                       # Pruebas unitarias
├── docs/
│   └── wsl2_gpu_setup.md        # Guía completa WSL2 + GPU + TensorFlow
├── Dockerfile                   # Imagen con soporte GPU
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Inicio Rápido

### Opción 1: Entorno Virtual Python

```bash
# Clonar repositorio
git clone https://github.com/TFM-OUTFIT-IA/stylemepal.git
cd stylemepal

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar entry point
python -m fashion_classifier
```

### Opción 2: Docker con GPU

```bash
# Construir imagen
docker compose build

# Ejecutar contenedor
docker compose up

# Ejecutar comando específico
docker compose run --rm app python -m fashion_classifier
```

---

## Notebooks

### 1. Entrenamiento (`01_training_polyvore_efficientnet.ipynb`)

Pipeline completo de entrenamiento con:
- Verificación de GPU en WSL2
- Carga del dataset Polyvore desde Hugging Face
- Data augmentation con `ImageDataGenerator`
- Transfer learning con EfficientNetB0
- Entrenamiento en 2 fases (frozen → fine-tuning)
- Evaluación en test y generación de artefactos

**Resultados:**
- Accuracy Top-1: **94.65%**
- Accuracy Top-3: **99.18%**
- Loss: **0.1786**

### 2. Inferencia (`02_inference_test.ipynb`)

Pruebas de inferencia con:
- Carga del modelo entrenado
- Predicción sobre imágenes de test
- Visualización de resultados
- Análisis de confianza

---

## Configuración GPU (WSL2)

Para ejecutar en Windows con GPU NVIDIA, consulta la guía completa: **[docs/wsl2_gpu_setup.md](docs/wsl2_gpu_setup.md)**

**Resumen rápido:**
```bash
# Verificar GPU
nvidia-smi

# Crear entorno con TensorFlow + GPU
python3 -m venv ~/tf
source ~/tf/bin/activate
pip install "tensorflow[and-cuda]"

# Verificar detección de GPU
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

---

## Modelo Entrenado

Archivo: `models/fashion_classifier_efficientnetb0_polyvore.keras`

**Arquitectura:**
- Base: EfficientNetB0 (preentrenado en ImageNet)
- Head personalizado: BatchNorm → Dropout → Dense(512) → Dense(256) → Dense(11)
- Parámetros totales: **4,846,766**
- Parámetros entrenables: **793,611**

**Categorías (11):**
`accessories`, `all-body`, `bags`, `bottoms`, `hats`, `jewellery`, `outerwear`, `scarves`, `shoes`, `sunglasses`, `tops`

---

## Dataset

- **Nombre**: Polyvore Fashion Dataset
- **Fuente**: Hugging Face (`owj0421/polyvore`)
- **Total**: 251,008 imágenes
- **Split**:
  - Train: 175,705
  - Validation: 37,651
  - Test: 37,652

---

## Desarrollo

### Agregar Nueva Funcionalidad

```bash
# Crear nueva rama
git checkout -b feature/nueva-funcionalidad

# Desarrollar en src/fashion_classifier/
# ...

# Commit y push
git add .
git commit -m "feat: descripción"
git push origin feature/nueva-funcionalidad
```

### Ejecutar Tests

```bash
pytest tests/
```

---

## Roadmap

- [ ] API REST con FastAPI para inferencia
- [ ] Frontend web para clasificación interactiva
- [ ] Fine-tuning para categorías adicionales
- [ ] Exportación a TensorFlow Lite (mobile)
- [ ] CI/CD con GitHub Actions
- [ ] Despliegue en cloud (AWS/GCP)

---

## Requisitos del Sistema

- **Sistema Operativo**: Windows 10/11 + WSL2 / Linux / macOS
- **Python**: 3.11+
- **GPU** (opcional pero recomendado): NVIDIA con CUDA support
- **RAM**: Mínimo 8GB (16GB recomendado)
- **Almacenamiento**: ~5GB para dataset + modelo

---

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'feat: descripción'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## Contacto

**Autor**: Ismael GM
**Proyecto**: TFM - Outfit AI
**Repositorio**: [https://github.com/TFM-OUTFIT-IA/stylemepal](https://github.com/TFM-OUTFIT-IA/stylemepal)

---

**Última actualización**: Febrero 2026
