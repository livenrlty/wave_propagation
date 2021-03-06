import torch
import torch.nn as nn
import torch.nn.functional as F
import random
import tqdm
import os
import numpy as np
import time
import logging
from utils.experiment import save_network
from utils.experiment_evaluator import save_sequence_plots, get_test_predictions_pairs
from utils.io import save_json


class ExperimentRunner(nn.Module):
    def __init__(self, experiment):
        super(ExperimentRunner, self).__init__()
        self.exp = experiment
        self.args = experiment.args
        self.model = experiment.model

        self.train_data = experiment.dataloaders['train']
        self.val_data = experiment.dataloaders['val']
        self.test_data = experiment.dataloaders['test']

        # if torch.cuda.device_count() > 1:
        #     self.model.to(self.exp.device)
        #     self.model = nn.DataParallel(module=self.model)
        # else:
        self.model = experiment.model
        self.model.to(self.exp.device)

        self.best_val_model_loss = experiment.logger.get_best_val_loss()
        self.refeed = False

    def get_num_parameters(self):
        total_num_params = 0
        for param in self.parameters():
            total_num_params += np.prod(param.shape)

        return total_num_params

    def run_batch_iter(self, batch_images, train):
        # Expects input of Batch Size x Video Length x Height x Width
        # Returns loss per each sequence prediction
        if train:
            self.model.train()
        else:
            self.model.eval()

        video_length = batch_images.size(1)
        random_starting_points = random.sample(range(video_length - self.args.num_input_frames - self.args.num_output_frames - 1), self.args.samples_per_sequence)

        batch_loss = 0
        for starting_point in random_starting_points:
            input_end_point = starting_point + self.args.num_input_frames
            input_frames = batch_images[:, starting_point:input_end_point, :, :].clone()
            output_frames = self.model.get_future_frames(input_frames, self.args.num_output_frames, self.refeed)
            target_frames = batch_images[:, input_end_point:(input_end_point + self.args.num_output_frames), :, :]
            # print('ER sizes out, tar', output_frames.size(), target_frames.size())
            loss = F.mse_loss(output_frames, target_frames)
            batch_loss += loss.item()

            if train:
                self.exp.lr_scheduler.optimizer.zero_grad()
                loss.backward()
                self.exp.lr_scheduler.optimizer.step()

            # if self.args.debug:
                # logging.info('EXP RUNNER out tar size %s %s' % (output_frames.size(), target_frames.size()))

        return batch_loss / self.args.samples_per_sequence  # mean batch loss

    def run_experiment(self):
        logging.info('Start training at epoch %s / %s' % (self.exp.starting_epoch, self.args.num_epochs))
        for epoch_num in range(self.exp.starting_epoch, self.args.num_epochs):
            logging.info('Epoch: %d' % epoch_num)
            epoch_start_time = time.time()
            current_epoch_losses = {"train_loss": [], "validation_loss": []}
            with tqdm.tqdm(total=len(self.train_data), ncols=40) as pbar_train:  # create a progress bar for training
                for batch_num, batch_images in enumerate(self.train_data):
                    # logging.info('BATCH: %d' % batch_num )
                    batch_start_time = time.time()
                    batch_images = batch_images.to(self.exp.device)
                    loss = self.run_batch_iter(batch_images, train=True)
                    current_epoch_losses["train_loss"].append(loss)
                    self.exp.logger.record_loss_batchwise(loss, batch_increment=1)
                    batch_time = time.time() - batch_start_time
                    pbar_train.update(1)
                    pbar_train.set_description("loss: {:.4f} time: {:.1f}s".format(loss, batch_time))
                    if self.args.debug:
                        break
            with tqdm.tqdm(total=len(self.val_data), ncols=40) as pbar_val:  #
                for batch_images in self.val_data:
                    batch_images = batch_images.to(self.exp.device)

                    with torch.no_grad():
                        loss = self.run_batch_iter(batch_images, train=False)
                    current_epoch_losses["validation_loss"].append(loss)  # add current iter loss to val loss list.
                    pbar_val.update(1)  # add 1 step to the progress bar
                    pbar_val.set_description("loss: {:.4f}".format(loss))
                    if self.args.debug:
                        break

            #  get mean of all metrics of current epoch metrics dict, to get them ready for storage and output on the terminal.
            current_train_loss = np.mean(current_epoch_losses['train_loss'])
            current_validation_loss = np.mean(current_epoch_losses['validation_loss'])
            self.exp.logger.record_epoch_losses(current_train_loss, current_validation_loss, epoch_num)
            self.exp.logger.save_to_json(self.exp.files['logger'])
            self.exp.logger.save_validation_loss_plot(self.exp.dirs['training'])
            self.exp.logger.save_batchwise_loss_plot(self.exp.dirs['training'])
            # self.exp.logger.save_train_progress_stats(self.exp.files['progress'])

            loss_string = "Train loss: {:.4f} | Validation loss: {:.4f}".format(current_train_loss, current_validation_loss)
            epoch_elapsed_time = "{:.4f}".format(time.time() - epoch_start_time)
            logging.info("Epoch {}/{}:\t{}\tTime elapsed {}s".format(epoch_num, self.args.num_epochs, loss_string, epoch_elapsed_time))

            save_network(self.model, self.exp.files['model_latest'])
            # Save if best model so far
            if current_validation_loss < self.best_val_model_loss:
                logging.info('Saving a better model. Previous loss: %.4f New loss: %.4f' % (self.best_val_model_loss, current_validation_loss))
                self.best_val_model_loss = current_validation_loss
                save_network(self.model, os.path.join(self.exp.files['model_best']))

            # Plot test predictions during training. Cool!
            output_frames, target_frames = get_test_predictions_pairs(self.model, self.refeed, batch_images, self.args.test_starting_point, self.args.num_total_output_frames)
            save_sequence_plots(epoch_num, self.args.test_starting_point, output_frames, target_frames, self.exp.dirs['training'], self.exp.normalizer, 'Training')

            self.exp.logger.save_training_progress(self.exp.files['progress'])
