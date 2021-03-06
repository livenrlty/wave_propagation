import pickle
import os
import json
import pandas as pd
import numpy
import matplotlib.pyplot as plt


def save_figure(destination, obj=None):
    plt.tight_layout()
    plt.savefig(destination)  # png
    # plt.savefig(destination + ".svg", format="svg")
    # save(obj, destination) if obj else None
    plt.close()


def save(obj, filename):
    filename += ".pickle" if ".pickle" not in filename else ""
    with open(filename, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load(filename):
    filename += ".pickle" if ".pickle" not in filename else ""
    with open(filename, 'rb') as handle:
        return pickle.load(handle)


def default(o):
    if isinstance(o, numpy.int64):
        return int(o)
    # return o
    # raise TypeError


def save_json(dict, filename):
    with open(filename, 'w') as fp:
        json.dump(dict, fp, default=default)
    fp.close()


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    f.close()
    return data


def read_stats(folder):
    df = pd.read_csv(os.path.join(folder, "summary.csv"))
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
