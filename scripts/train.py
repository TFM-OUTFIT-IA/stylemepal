#!/usr/bin/env python3
"""Script automatizado de entrenamiento del clasificador de moda.

Uso:
    python scripts/train.py --epochs 50 --batch-size 64
"""

import argparse
import sys
from pathlib import Path

# Agregar src/ al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def main():
    parser = argparse.ArgumentParser(
        description='Entrenar Fashion Classifier'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=20,
        help='Número de épocas (default: 20)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        help='Tamaño de batch (default: 64)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('models'),
        help='Directorio de salida del modelo (default: models/)'
    )

    args = parser.parse_args()

    print(f"Iniciando entrenamiento...")
    print(f"  Épocas: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Output: {args.output_dir}")
    print()
    print("TODO: Implementar lógica de entrenamiento")
    print("Referencia: notebooks/01_training_polyvore_efficientnet.ipynb")


if __name__ == '__main__':
    main()
