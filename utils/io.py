import pickle
import os
import csv
import torch
import json
import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
from utils.helper_functions import normalize_image

def save(obj, filename):
    filename += ".pickle" if ".pickle" not in filename else ""
    with open(filename, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load(filename):
    filename += ".pickle" if ".pickle" not in filename else ""
    with open(filename, 'rb') as handle:
        return pickle.load(handle)

def figure_save(destination, obj=None):
    plt.savefig(destination) # png
    plt.savefig(destination + ".svg", format="svg")
    save(obj, destination) if obj else None


def imshow(image, title=None, smoothen=False, return_np=False, obj=None, normalize=None):
    """Imshow for Tensor."""
    num_channels = image.size()[0]

    if num_channels == 3:
        image = image.numpy().transpose((1, 2, 0))
        smooth_filter = (.5, .5, 0)
    elif num_channels == 1:
        image = image[0,:,:].numpy()
        smooth_filter = (.5, .5)
    else:
        raise Exception('Image size not supported ', image.size())

    if smoothen:
        image = ndimage.gaussian_filter(image, sigma=smooth_filter)

    # image = np.clip(image, 0, 1)
    if obj is not None:
        obj.imshow(image, cmap='gray', interpolation='none')
        obj.axis("off")
        if title is not None:
            obj.set_title(title)
    else:
        plt.imshow(image, cmap='gray', interpolation='none')
        plt.axis("off")
        if title is not None:
            plt.title(title)
    if return_np:
        return image

###### EXPERIMENT BUILDER STUFF FROM HERE


def save_as_json(dict, filename):
    with open(filename, 'w') as f:
        f.write("%s" % json.dumps(dict))
    f.close()

def read_stats(folder):
    df = pd.read_csv(os.path.join(folder,"summary.csv"))
    dicc = {}
    for c in df.columns:
        dicc[c] = df[c].values
    return dicc

def save_to_stats_pkl_file(experiment_log_filepath, filename, stats_dict):
    summary_filename = os.path.join(experiment_log_filepath, filename)
    with open("{}.pkl".format(summary_filename), "wb") as file_writer:
        pickle.dump(stats_dict, file_writer)


def load_from_stats_pkl_file(experiment_log_filepath, filename):
    summary_filename = os.path.join(experiment_log_filepath, filename)
    with open("{}.pkl".format(summary_filename), "rb") as file_reader:
        stats = pickle.load(file_reader)

    return stats
