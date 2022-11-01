# EvoAug Analysis

This repository performs the analysis from "Evolution-inspired augmentations improve deep learning for regulatory genomics" by Nicholas Keone Lee, Ziqi (Amber) Tang, Shushan Toneyan, and Peter K Koo. 

For questions, email: koo@cshl.edu

<img src="fig/augmentations.png" alt="fig" width="500"/>

<img src="fig/overview.png" alt="overview" width="500"/>



#### Install:
```
pip install git+https://github.com/p-koo/evoaug_analysis.git
```

#### Dependencies:

```
torch 1.12.1+cu113
pytorch_lightning 1.7.7
evoaug
sklearn 1.0.2
scipy 1.7.3
h5py 3.1.0
pandas 1.3.5
matplotlib 3.2.2
logomaker 0.8
numpy 1.21.6
```


#### Reproducible analyses:

The code to reproduce the analyses is in the directory: analysis. Data can be downloaded into analysis/data by running download_data.sh. The main analyses for Basset, DeepSTARR, and ChIP-seq is in analysis/main. The parameter sweeps used to determine optimal settings can be found in analysis/supp. All results are stored in analysis/results. 

#### Examples on Google Colab:

DeepSTARR analysis:
```
https://colab.research.google.com/drive/1a2fiRPBd1xvoJf0WNiMUgTYiLTs1XETf?usp=sharing
```

ChIP-seq analysis:
```
https://colab.research.google.com/drive/1GZ8v4Tq3LQMZI30qvdhF7ZW6Kf5GDyKX?usp=sharing
```

Basset analysis: data is too large for colab =(








