# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-15

### Agregado
- Notebook de entrenamiento completo (01_training_polyvore_efficientnet.ipynb)
- Notebook de inferencia y visualización (02_inference_test.ipynb)
- Modelo EfficientNetB0 entrenado en Polyvore (94.65% accuracy)
- Label encoder para mapeo de categorías
- 14 imágenes de prueba en data/external/test_images/
- Artefactos de entrenamiento (matrices, gráficas, métricas)
- Documentación completa de configuración WSL2+GPU
- Dockerfile con soporte para TensorFlow GPU
- requirements.txt con todas las dependencias

### Cambiado
- Renombrado paquete de `outfit_ai` a `fashion_classifier`
- Actualizado README con documentación completa fusionada
- Mejorado .gitignore con patrones específicos para ML

### Migrado
- Código desde repositorio fashion-image-classifier
- Estructura adaptada a arquitectura profesional TFM
