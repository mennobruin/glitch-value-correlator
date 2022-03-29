import matplotlib.pyplot as plt
from resources.constants import PLOT_DIR


def plot_histogram(data, save=False):
    pass


def plot_channel(channel, data, data_type, save=False, score=None):
    f_name = f'{score}_{channel}+{data_type}'

    fig = plt.figure(figsize=(10, 8), dpi=200)

    plt.title(f_name)
    plt.bar(data.xgrid, data.counts, width=data.span / data.nbin)
    plt.xlim([data.offset, data.offset + data.span])

    if save:
        fig.savefig(PLOT_DIR + f_name + '.png', dpi=fig.dpi)
    else:
        plt.show()
    plt.clf()