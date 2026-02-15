#!/usr/bin/env python3
"""Script de inferencia para clasificar imágenes de moda.

Uso:
    python scripts/predict.py --image path/to/image.jpg
    python scripts/predict.py --image-dir data/external/test_images/
"""

import argparse
import sys
from pathlib import Path

# Agregar src/ al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def main():
    parser = argparse.ArgumentParser(
        description='Clasificar imágenes de moda'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--image',
        type=Path,
        help='Path a imagen individual'
    )
    group.add_argument(
        '--image-dir',
        type=Path,
        help='Directorio con múltiples imágenes'
    )
    parser.add_argument(
        '--model',
        type=Path,
        default=Path('models/fashion_classifier_efficientnetb0_polyvore.keras'),
        help='Path al modelo (default: models/fashion_classifier_*.keras)'
    )

    args = parser.parse_args()

    print(f"Clasificador de Moda")
    print(f"  Modelo: {args.model}")
    if args.image:
        print(f"  Imagen: {args.image}")
    else:
        print(f"  Directorio: {args.image_dir}")
    print()
    print("TODO: Implementar lógica de inferencia")
    print("Referencia: notebooks/02_inference_test.ipynb")


if __name__ == '__main__':
    main()
