import os, sys
import numpy as np
import torch
import pytorch_lightning as pl
from six.moves import cPickle
from evoaug import evoaug, augment

sys.path.append('../../evoaug_analysis')
import utils
from model_zoo import DeepSTARR

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# load data
expt_name = 'DeepSTARR'
data_path = '../data'
filepath = os.path.join(data_path, expt_name + '_data.h5')
data_module = utils.H5DataModule(filepath, batch_size=100, lower_case=False)

expt_name += '_noi'

output_dir = '../results/deepSTARR_hyperparm_sweep'
utils.make_directory(output_dir)

noise_std_range = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
num_trials = 5 

all_aug_results = {}
all_finetune_results = {}
for n, noise_std in enumerate(noise_std_range):

    trial_aug_results = []
    trial_finetune_results = []
    for trial in range(num_trials):

        deepstarr = DeepSTARR(data_module.y_train.shape[-1]).to(device)
        loss = torch.nn.MSELoss()
        optimizer_dict = utils.configure_optimizer(deepstarr, 
                                                   lr=0.001, 
                                                   weight_decay=1e-6, 
                                                   decay_factor=0.1, 
                                                   patience=5, 
                                                   monitor='val_loss')

        augment_list = [
            #augment.RandomDeletion(delete_min=0, delete_max=30),
            #augment.RandomRC(rc_prob=0.5),
            #augment.RandomInsertion(insert_min=0, insert_max=30),
            #augment.RandomTranslocation(shift_min=0, shift_max=30),
            augment.RandomNoise(noise_mean=0, noise_std=noise_std),
        ]
        robust_deepstarr = evoaug.RobustModel(deepstarr,
                                       criterion=loss,
                                       optimizer=optimizer_dict, 
                                       augment_list=augment_list,
                                       max_augs_per_seq=2, 
                                       hard_aug=True, 
                                       inference_aug=False)

        # create pytorch lightning trainer
        ckpt_aug_path = expt_name+"_aug_"+str(n)+'_'+str(trial)
        callback_topmodel = pl.callbacks.ModelCheckpoint(monitor='val_loss', 
                                                         save_top_k=1, 
                                                         dirpath=output_dir, 
                                                         filename=ckpt_aug_path)
        callback_es = pl.callbacks.early_stopping.EarlyStopping(monitor='val_loss', patience=10)
        trainer = pl.Trainer(gpus=1, max_epochs=100, auto_select_gpus=True, logger=None, 
                            callbacks=[callback_es, callback_topmodel])

        # fit model
        trainer.fit(robust_deepstarr, datamodule=data_module)

        # load checkpoint for model with best validation performance
        model_path = os.path.join(output_dir, ckpt_aug_path+'.ckpt')
        robust_deepstarr = evoaug.load_model_from_checkpoint(robust_deepstarr, model_path)

        # evaluate best model
        pred = utils.get_predictions(robust_deepstarr, data_module.x_valid, batch_size=100)
        aug_results = utils.evaluate_model(data_module.y_valid, pred, task='regression')   # task is 'binary' or 'regression'

        # change to fine-tune mode
        finetune_optimizer = torch.optim.Adam(filter(lambda p: p.requires_grad, robust_deepstarr.model.parameters()),
                                                   lr=0.0001, weight_decay=1e-6)
        robust_deepstarr.finetune_mode(optimizer=finetune_optimizer)

        # set up trainer for fine-tuning
        ckpt_finetune_path = expt_name+"_finetune_"+str(n)+'_'+str(trial)
        callback_topmodel = pl.callbacks.ModelCheckpoint(monitor='val_loss', 
                                                         save_top_k=1, 
                                                         dirpath=output_dir, 
                                                         filename=ckpt_finetune_path)
        trainer = pl.Trainer(gpus=1, max_epochs=5, auto_select_gpus=True, logger=None, 
                            callbacks=[callback_topmodel])

        # Fine-tune model
        trainer.fit(robust_deepstarr, datamodule=data_module)

        # load checkpoint for model with best validation performance
        model_path = os.path.join(output_dir, ckpt_finetune_path+'.ckpt')
        robust_deepstarr = evoaug.load_model_from_checkpoint(robust_deepstarr, model_path)

        # evaluate best model
        pred = utils.get_predictions(robust_deepstarr, data_module.x_valid, batch_size=100)
        finetune_results = utils.evaluate_model(data_module.y_valid, pred, task='regression') # task is 'binary' or 'regression'


        trial_aug_results.append(aug_results)
        trial_finetune_results.append(finetune_results)

    all_aug_results[n] = trial_aug_results
    all_finetune_results[n] = trial_finetune_results


with open(os.path.join(output_dir, 'noise_sweep.pickle'), 'wb') as fout:
    cPickle.dump(all_finetune_results, fout)
    cPickle.dump(all_aug_results, fout)


    