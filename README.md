# Outfit AI (TFM)

Proyecto de investigacion/desarrollo para el TFM. Estructura base pensada para trabajo con datos, modelos y experimentos.

## Estructura

Estructura base:

```
.
├─ src/
│  └─ outfit_ai/         # Paquete principal (codigo productivo)
│     ├─ __init__.py
│     └─ __main__.py      # Entry point: python -m outfit_ai
├─ data/
│  ├─ raw/               # Datos crudos, sin transformar (no versionar grandes)
│  ├─ processed/         # Datos limpios/featureados (no versionar grandes)
│  └─ external/          # Fuentes externas y descargas
├─ models/               # Modelos entrenados
├─ notebooks/            # Analisis exploratorio y prototipos
├─ scripts/              # Entrenamiento, ETL, evaluacion, utilidades
├─ reports/
│  └─ figures/           # Figuras para informes
├─ tests/                # Pruebas unitarias/integracion
├─ docs/                 # Documentacion adicional
├─ requirements.txt      # Dependencias
└─ README.md             # Guia rapida del proyecto
```

Guia rapida por carpeta:

- `src/` Contiene el codigo estable y reutilizable. Todo lo que quieras importar debe vivir aqui.
- `data/` Estructura de datos por etapas. Evita subir datasets grandes; usa enlaces o scripts de descarga.
- `models/` Guardado de pesos, checkpoints y artefactos de entrenamiento.
- `notebooks/` Notebooks de investigacion. Recomiendo nombres con fecha y objetivo (ej: `2026-02-07-eda-dataset.ipynb`).
- `scripts/` Entradas ejecutables (ETL, entrenamiento, evaluacion). Mantenerlos simples y delegar logica a `src/`.
- `reports/` Resultados y figuras finales para el TFM.
- `tests/` Pruebas para asegurar calidad y evitar regresiones.
- `docs/` Documentacion extendida, decisiones tecnicas, etc.

## Requisitos

- Python 3.10+ recomendado.

## Puesta en marcha rapida

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Docker (desarrollo)

Construir y ejecutar:

```bash
docker compose build
docker compose up
```

Ejecutar un comando puntual:

```bash
docker compose run --rm app python -m outfit_ai
```

## Notas

- Actualiza este README con el objetivo, dataset y metrica principal del TFM.
