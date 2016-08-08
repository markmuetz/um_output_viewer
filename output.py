from os import path
import pylab as plt

def multi_timeseries(timeseries_list, filename):
    f, axes = plt.subplots(1, len(timeseries_list))
    for i, (name, timeseries) in enumerate(timeseries_list):
        axes[i].set_title(name)
        axes[i].plot(timeseries)
    plt.savefig(filename)
