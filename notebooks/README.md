# 👗 Sistema de Recomendación de Moda con Deep Learning

Este proyecto implementa un sistema completo de análisis y recomendación de outfits de moda utilizando técnicas de Deep Learning. Está construido sobre el dataset **Polyvore Outfits (2018)**, que contiene más de 250,000 prendas etiquetadas con 11 categorías.

---

## 📋 Descripción General

El proyecto se compone de **cuatro notebooks** que trabajan en conjunto. Tres de ellos forman un pipeline secuencial, mientras que uno funciona de forma completamente independiente.

---

## 🛠️ Configuración del Entorno

Sigue estos pasos **en orden** para crear el entorno virtual e instalar todas las dependencias correctamente.

### Requisitos previos del sistema

- Python 3.10 o superior
- GPU NVIDIA con drivers actualizados (recomendado: CUDA 12.1+)
- Git (para clonar el repositorio si aplica)

### Paso 1 — Crear el entorno virtual en el directorio del proyecto

Abre una terminal en la **raíz del proyecto** (donde están los notebooks) y ejecuta:

```bash
# Crear el entorno virtual llamado 'venv' dentro del proyecto
python -m venv venv
```

### Paso 2 — Activar el entorno virtual

**En Windows (CMD o PowerShell):**
```bash
venv\Scripts\activate
```

**En Linux / macOS:**
```bash
source venv/bin/activate
```

> Una vez activado, el prefijo `(venv)` aparecerá al inicio de la línea en tu terminal.

### Paso 3 — Actualizar pip

```bash
pip install --upgrade pip
```

### Paso 4 — Instalar PyTorch con soporte CUDA ⚡

> ⚠️ Este paso es **crítico** y debe realizarse **antes** de instalar el resto de dependencias. PyTorch con CUDA **no puede** instalarse desde el `requirements.txt` directamente.

```bash
# Para CUDA 12.1 (recomendado, compatible con RTX 30xx / 40xx)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

Si tu GPU usa CUDA 11.8:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Para verificar que PyTorch detecta la GPU correctamente:
```bash
python -c "import torch; print('CUDA disponible:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

### Paso 6 — Instalar el resto de dependencias

```bash
pip install -r requirements.txt
```
---

### 📋 Resumen rápido de todos los comandos

```bash
# 1. Crear y activar el entorno
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# 2. Actualizar pip
pip install --upgrade pip

# 3. PyTorch con CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. PyTorch Geometric
pip install torch_geometric
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv \
    -f https://data.pyg.org/whl/torch-2.4.0+cu121.html

# 5. Resto de dependencias
pip install -r requirements.txt

# 6. Registrar kernel y lanzar Jupyter
python -m ipykernel install --user --name=venv --display-name "Python (fashion-venv)"
jupyter notebook
```

---

## ⚙️ Orden de Ejecución

> ⚠️ **IMPORTANTE**: Los notebooks deben ejecutarse en el siguiente orden. El primer notebook genera un archivo `.parquet` con los embeddings de FashionCLIP que es requerido por los notebooks 2 y 3.

```
1️⃣  garment_feature_extraction_fashionclip.ipynb   ← PRIMERO (genera el .parquet)
        │
        ├──▶  2️⃣  garment_category_classification_fashionclip.ipynb
        │
        └──▶  3️⃣  outfit_recommendation_RGCN.ipynb

4️⃣  garment_category_classification_effecientNet.ipynb   ← INDEPENDIENTE (puede ejecutarse en cualquier momento)
```

---

## 📓 Descripción de cada Notebook

---

### 1️⃣ `garment_feature_extraction_fashionclip.ipynb`
**Extracción de características visuales y metadata dinámica con FashionCLIP**

Este es el **notebook fundacional** del pipeline. Su objetivo es procesar todas las imágenes del dataset Polyvore y convertirlas en representaciones numéricas (embeddings) que puedan ser consumidas por los modelos posteriores.

**¿Qué hace?**

- Carga el dataset `owj0421/polyvore` desde HuggingFace, que contiene más de 250,000 prendas de moda con sus imágenes y categorías.
- Carga el modelo preentrenado **FashionCLIP** (`patrickjohncyh/fashion-clip`), una variante de CLIP especializada en moda.
- Para cada imagen del dataset, extrae un **vector de embedding visual de 512 dimensiones**.
- Adicionalmente, realiza tareas de **Zero-Shot** (clasificación sin entrenamiento previo) usando prompts de texto para inferir automáticamente:
  - **Estilo** de la prenda: Casual, Formal, Streetwear, Bohemian, Sporty, Elegant, Vintage o Minimalist.
  - **Temporada/Clima** adecuado: Summer, Winter o Transitional.
- Procesa las imágenes en lotes (batch size = 64) para eficiencia.
- Guarda todos los resultados (image_id, category, style, weather, embedding) en un archivo **`polyvore_fashionclip_features.parquet`**.

**Salida generada:**
```
📄 polyvore_fashionclip_features.parquet  ← Requerido por los notebooks 2 y 3
```

**Tecnologías:** PyTorch, HuggingFace Transformers, HuggingFace Datasets, CLIP, Pandas, PyArrow

---

### 2️⃣ `garment_category_classification_fashionclip.ipynb`
**Clasificación de categorías de prendas usando embeddings de FashionCLIP**

> ⚠️ **Requiere:** `polyvore_fashionclip_features.parquet` (generado por el notebook 1)

Este notebook entrena un **clasificador neuronal ligero** que, partiendo de los embeddings de 512 dimensiones generados por FashionCLIP, aprende a predecir la categoría de una prenda (por ejemplo: tops, bottoms, shoes, bags, etc.).

**¿Qué hace?**

- Lee el archivo `.parquet` generado en el paso anterior y carga los embeddings y las etiquetas de categoría.
- Utiliza un `LabelEncoder` (previamente guardado) para codificar las 11 categorías en valores numéricos.
- Divide el dataset en tres conjuntos: **80% entrenamiento**, **10% validación** y **10% test**.
- Define una red neuronal simple (`nn.Sequential`) de dos capas densas con BatchNorm, ReLU y Dropout:
  - Capa 1: 512 → 256 neuronas
  - Capa 2: 256 → 11 neuronas (una por categoría)
- Entrena el modelo durante **25 épocas** con el optimizador Adam y CrossEntropyLoss.
- Guarda el mejor modelo según la pérdida de validación en `fashion_classifier_fashionclip_polyvore.pth`.
- Evalúa el accuracy final sobre el conjunto de test.
- Genera una **gráfica de curvas de pérdida** (train vs. validation) y la guarda como imagen PNG.

**La ventaja de este enfoque** es su eficiencia: al trabajar directamente con embeddings precomputados en lugar de imágenes crudas, el entrenamiento es extremadamente rápido incluso sin GPU potente.

**Salida generada:**
```
🧠 fashion_classifier_fashionclip.pth         ← Pesos del modelo entrenado
📊 category_probe_loss_curve.png              ← Gráfica de entrenamiento
```

**Tecnologías:** PyTorch, Scikit-learn, Pandas, NumPy, Matplotlib

---

### 3️⃣ `outfit_recommendation_RGCN.ipynb`
**Sistema de recomendación de outfits completos usando Redes Neuronales de Grafos (RGCN)**

> ⚠️ **Requiere:** `polyvore_fashionclip_features.parquet` (generado por el notebook 1)

Este es el **notebook más avanzado y complejo** del proyecto. Su objetivo es construir un sistema que aprenda la *compatibilidad* entre prendas y sea capaz de recomendar un outfit completo dado un artículo inicial (por ejemplo, dada una camisa, recomendar unos pantalones, zapatos y chaqueta que combinen bien).

**¿Qué hace?**

**Construcción del Grafo de Moda:**
- Carga los embeddings del `.parquet` y los usa como nodos del grafo, donde cada prenda es un nodo con su vector de 512 dimensiones como característica.
- Carga el dataset `owj0421/polyvore-outfits` que contiene outfits reales compatibles e incompatibles.
- Construye las **aristas (edges)** del grafo: dos prendas están conectadas si aparecen juntas en un outfit compatible.
- Asigna un **tipo de relación diferente a cada par de categorías** (e.g., tops↔bottoms, shoes↔bags). Esto es clave: el modelo no asume una compatibilidad universal, sino que aprende reglas específicas por tipo de prenda (idea tomada del paper de Vasileva et al., ECCV 2018).

**Modelo FashionRGCN:**
- Implementa una **Red Neuronal de Grafos Convolucional Relacional (RGCN)** con dos capas:
  - Capa 1: comprime los embeddings de 512 → 256 dimensiones.
  - Capa 2: comprime de 256 → 128 dimensiones.
- Las capas RGCN permiten que cada nodo agregue información de sus vecinos **de forma diferente según el tipo de relación**, capturando así las reglas de compatibilidad específicas entre categorías.

**Entrenamiento con Triplet Loss:**
- Entrena con una **función de pérdida triplete** (`triplet_loss`) con un margen de 0.2.
- Cada triplete consiste en: *ancla* (prenda base) + *positivo* (prenda compatible) + *negativo* (prenda incompatible).
- Implementa dos estrategias de muestreo de negativos:
  - **Easy Negatives**: muestrea negativos al azar.
  - **Hard Negatives**: muestrea negativos de la misma categoría que el positivo (más difícil de distinguir, fuerza al modelo a aprender diferencias de estilo).
- Incluye **Early Stopping** para evitar sobreajuste.

**Validación y Análisis:**
- Realiza un experimento de **Zero-Shot Baseline** para comparar los embeddings crudos de CLIP contra los embeddings refinados por el RGCN. Los resultados muestran que el RGCN reduce la pérdida triplete de 0.1466 (CLIP puro) a ~0.0024, con una tasa de acierto del 99%.
- Genera visualizaciones con **t-SNE** para ver cómo el espacio de embeddings agrupa las categorías.
- Visualiza histogramas de distancias entre pares compatibles e incompatibles.

**Simulación de "StylemePal" (Armario Virtual):**
- Incluye un pipeline de inferencia completo que permite digitalizar un armario personal con imágenes reales.
- Dado un artículo ancla (e.g., una camiseta), el sistema recomienda las prendas del armario que mejor combinan usando búsqueda por similitud de coseno en el espacio de embeddings del RGCN.

**Salida generada:**
```
🧠 best_fashion_rgcn_easy_negatives.pth   ← Pesos del modelo RGCN entrenado
💾 train_graph_data.pt                    ← Grafo de entrenamiento serializado
💾 test_graph_data.pt                     ← Grafo de test serializado
```

**Tecnologías:** PyTorch, PyTorch Geometric (RGCN, Data, NeighborLoader), Scikit-learn (t-SNE), HuggingFace, Matplotlib, Seaborn

---

### 4️⃣ `garment_category_classification_effecientNet.ipynb`
**Clasificación de imágenes de moda con EfficientNetB0 y Transfer Learning**

> ✅ **Completamente independiente**: No requiere ningún otro notebook. Puede ejecutarse en cualquier orden.

Este notebook aborda el mismo problema de clasificación de categorías que el notebook 2, pero con un enfoque radicalmente diferente: **trabaja directamente con las imágenes en píxeles** y utiliza Transfer Learning sobre EfficientNetB0 (preentrenado en ImageNet). Es el enfoque más completo y cercano a un pipeline de producción.

**¿Qué hace?**

**Preparación del entorno:**
- Verifica que el entorno tiene GPU disponible (está optimizado para WSL + RTX 3080).
- Activa **Mixed Precision (FP16)** para acelerar el entrenamiento y reducir el uso de VRAM.
- Configura el cache de HuggingFace para la carga del dataset.

**Carga y exploración del dataset:**
- Carga directamente el dataset `owj0421/polyvore` desde HuggingFace.
- Visualiza la distribución de las 11 categorías con gráficas de barras horizontales.
- Muestra muestras aleatorias de imágenes del dataset.

**Preprocesamiento con Lazy Loading:**
- Implementa un generador de datos (`data_generator`) que aplica **carga perezosa** (lazy loading): las imágenes se procesan imagen por imagen durante el entrenamiento, evitando cargar las 250k imágenes en RAM simultáneamente.
- Las imágenes se redimensionan a 224×224 píxeles (compatible con EfficientNet) y se normalizan.
- Aplica **Data Augmentation** en el set de entrenamiento: rotaciones, desplazamientos, flips horizontales y zoom.
- División estratificada: **70% entrenamiento**, **15% validación**, **15% test**.

**Modelo con Transfer Learning en dos fases:**

*Fase 1 – Feature Extraction (capas congeladas):*
- Carga **EfficientNetB0** preentrenado en ImageNet con `include_top=False`.
- Congela todos los pesos del modelo base.
- Añade capas densas propias encima: Dense(512) → BN → Dropout(0.5) → Dense(256) → Dropout(0.3) → Dense(11, softmax).
- Entrena solo las capas nuevas durante 10 épocas con lr=1e-3.

*Fase 2 – Fine-Tuning (capas descongeladas):*
- Descongela las últimas **100 capas** de EfficientNetB0.
- Re-entrena con lr=1e-5 durante hasta 15 épocas adicionales.
- Usa callbacks: EarlyStopping (patience=7), ReduceLROnPlateau y ModelCheckpoint.

**Evaluación exhaustiva:**
- Evalúa en el test set reportando **Accuracy Top-1** y **Accuracy Top-3**.
- Genera un `classification_report` detallado por categoría (precision, recall, F1).
- Visualiza una **Matriz de Confusión Normalizada** con un mapa de calor.
- Muestra predicciones aleatorias con confianza para análisis cualitativo.

**Inferencia para nuevas imágenes:**
- Incluye la función `predict_image()` lista para producción, que acepta una ruta de archivo o un objeto PIL y retorna el Top-K de predicciones con sus probabilidades.

**Salida generada:**
```
🧠 fashion_classifier_final.keras       ← Modelo completo para producción
🔖 label_encoder.pkl                    ← Codificador de categorías
📊 training_history.png                 ← Curvas de accuracy y loss (ambas fases)
📊 confusion_matrix.png                 ← Matriz de confusión normalizada
📊 predictions_visualization.png        ← Visualización de predicciones
📄 model_metrics.json                   ← Métricas finales en JSON
```

**Tecnologías:** TensorFlow/Keras, EfficientNetB0, Scikit-learn, HuggingFace Datasets, Pillow, Matplotlib, Seaborn, Mixed Precision (FP16)

---

## 📦 Dependencias Principales

| Librería | Uso |
|---|---|
| `torch` / `torchvision` | Modelos PyTorch, RGCN |
| `torch_geometric` | Redes Neuronales de Grafos (RGCN) |
| `tensorflow` / `keras` | Modelo EfficientNet |
| `transformers` | FashionCLIP |
| `datasets` | Carga de Polyvore desde HuggingFace |
| `scikit-learn` | Métricas, t-SNE, LabelEncoder |
| `pandas` / `pyarrow` | Manejo de datos y formato Parquet |
| `PIL` / `Pillow` | Procesamiento de imágenes |
| `matplotlib` / `seaborn` | Visualizaciones |

---

## 📚 Referencias

- **FashionCLIP**: [patrickjohncyh/fashion-clip](https://huggingface.co/patrickjohncyh/fashion-clip)
- **Polyvore Dataset**: [owj0421/polyvore](https://huggingface.co/datasets/owj0421/polyvore)
- **Polyvore Outfits Dataset**: [owj0421/polyvore-outfits](https://huggingface.co/datasets/owj0421/polyvore-outfits)
- Vasileva et al., *"Learning Type-Aware Embeddings for Fashion Compatibility"*, ECCV 2018
- Han et al., *"Learning Fashion Compatibility with Bidirectional LSTMs"*, MM 2017
