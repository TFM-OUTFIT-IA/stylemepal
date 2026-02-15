"""Setup configuration for Fashion Classifier package."""

from pathlib import Path
from setuptools import setup, find_packages

# Leer README para descripción larga
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='fashion-classifier',
    version='0.1.0',
    author='Ismael GM',
    author_email='your.email@example.com',
    description='Sistema de clasificación de imágenes de moda con Deep Learning',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TFM-OUTFIT-IA/stylemepal',
    project_urls={
        'Bug Reports': 'https://github.com/TFM-OUTFIT-IA/stylemepal/issues',
        'Source': 'https://github.com/TFM-OUTFIT-IA/stylemepal',
    },
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.11',
    install_requires=[
        'tensorflow[and-cuda]==2.15.0',
        'numpy>=1.24.3',
        'pandas>=2.1.4',
        'pillow>=10.2.0',
        'matplotlib>=3.8.2',
        'seaborn>=0.13.1',
        'scikit-learn>=1.4.0',
        'datasets>=2.16.1',
    ],
    extras_require={
        'dev': [
            'jupyter>=1.0.0',
            'ipykernel>=6.29.0',
            'black>=24.1.1',
            'flake8>=7.0.0',
            'pytest>=7.4.4',
        ],
    },
    entry_points={
        'console_scripts': [
            'fashion-classifier=fashion_classifier.__main__:main',
        ],
    },
)
