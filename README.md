# Outfit AI (TFM)

Proyecto de investigacion/desarrollo para el TFM. Estructura base pensada para trabajo con datos, modelos y experimentos.

## Estructura

- `src/` Codigo fuente del proyecto.
- `data/` Datos (raw/processed/external). No se versionan datasets grandes.
- `models/` Modelos entrenados y artefactos.
- `notebooks/` Notebooks exploratorios.
- `scripts/` Scripts de entrenamiento/ETL/utilidades.
- `reports/` Informes y figuras.
- `tests/` Pruebas.
- `docs/` Documentacion.

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
