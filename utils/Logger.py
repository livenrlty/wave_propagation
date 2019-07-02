import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils.io import figure_save, save_json
import os


class Logger():
    """
    Saves network data for later analasys. Epochwise loss, Batchwise loss, Accuracy (not currently in use) and
    Validation loss
    """
    def __init__(self):
        self.logs = {'train_loss': [],
                     'validation_loss': [],
                     'epoch_nr': [],
                     'batch_loss': [],
                     'batch_nr': []
                     }

    def record_epoch_losses(self, train_loss, val_loss, epoch):
        """
        Creates two lists, one of losses and one of index of epoch
        """
        self.logs['train_loss'].append(train_loss)
        self.logs['validation_loss'].append(val_loss)
        self.logs['epoch_nr'].append(epoch)

    def record_loss_batchwise(self, loss, batch_increment=1):
        """
        Creates two lists, one of losses and one of index of batch
        """
        if len(self.logs['batch_nr']) > 0:
            batch_num = self.logs['batch_nr'][-1] + batch_increment  # increase by one
        else:
            batch_num = 0
        self.logs['batch_loss'].append(loss)
        self.logs['batch_nr'].append(batch_num)

    def get_best_val_loss(self):
        return max(self.logs['validation_loss'])

    def get_current_epoch_loss(self, type):
        return self.logs['%s_loss' % type][-1]

    def save_train_loss_plot(self, figures_dir):
        fig = plt.figure().add_axes()
        sns.set(style="darkgrid")  # darkgrid, whitegrid, dark, white, and ticks
        sns.set_context("talk")
        data = {}
        data.update({"Epoch": self.logs['train_epoch_nr'], "Loss": self.logs['train_loss']})
        sns.lineplot(x="Epoch", y="Loss",
                     data=pd.DataFrame.from_dict(data), ax=fig)
        figure_save(os.path.join(figures_dir, "Epoch_Loss"), obj=fig)

    def save_batchwise_loss_plot(self, figures_dir):
        fig = plt.figure().add_axes()
        sns.set(style="darkgrid")  # darkgrid, whitegrid, dark, white, and ticks
        sns.set_context("talk")
        data = {}
        data.update({"Batch": self.logs['batch_nr'], "Loss": self.logs['batch_loss']})
        sns.lineplot(x="Batch", y="Loss",
                     data=pd.DataFrame.from_dict(data), ax=fig)
        figure_save(os.path.join(figures_dir, "Batch_Loss"), obj=fig)

    def save_validation_loss_plot(self, figures_dir):
        """
        Plots validation and epoch loss next to each other
        """
        hue = []
        loss = []
        nr = []
        for i, element in enumerate(self.logs['train_loss']):
            loss.append(element)
            nr.append(self.logs['train_epoch_nr'][i])
            hue.append("Training")
        for i, element in enumerate(self.logs['validation_loss']):
            loss.append(element)
            nr.append(self.logs['validation_epoch_nr'][i])
            hue.append("Validation")
        fig = plt.figure().add_axes()
        sns.set(style="darkgrid")  # darkgrid, whitegrid, dark, white, and ticks
        sns.set_context("talk")
        data = {}
        data.update({"Epoch": nr, "Loss": loss, "Dataset": hue})
        sns.lineplot(x="Epoch", y="Loss", hue="Dataset", data=pd.DataFrame.from_dict(data), ax=fig)
        figure_save(os.path.join(figures_dir, "Validation_Loss"), obj=fig)

    def load_from_json(self, filename):
        pass

    def save_to_json(self, filename):
        save_json(self.logs, filename)