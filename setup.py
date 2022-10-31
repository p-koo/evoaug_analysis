from setuptools import setup, find_packages


setup(
    name="evoaug_analysis",
    version="0.1.0",
    packages=find_packages(),
    description = "Code to analyze genomics datasets with deep learning models trained with evolution-inspired data augmentations. ",
    python_requires=">=3.6",
    install_requires=[
        'torch 1.12.1+cu113',
        'pytorch_lightning 1.7.7',
        'evoaug',
        'sklearn 1.0.2',
        'scipy 1.7.3',
        'h5py 3.1.0',
        'pandas 1.3.5',
        'matplotlib 3.2.2',
        'logomaker 0.8',
        ],
)
