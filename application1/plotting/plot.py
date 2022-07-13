import matplotlib.pyplot as plt
from resources.constants import PLOT_DIR
from application1.config import config_manager


LOG = config_manager.get_logger(__name__)


def plot_histogram(channel, transformation, histogram, data_type, xlabel='x', ylabel='Counts (#)', label=None, save=False, rank=None, fig=None, return_fig=False, block=False):
    label = label if label else data_type
    transformation = transformation if transformation != '' else 'none'
    f_name = f'{rank}_{channel}_{transformation}+{data_type}'
    LOG.info(f'Plotting {f_name}...')

    if not fig:
        fig = plt.figure(figsize=(10, 8))

    plt.rcParams['font.size'] = 16
    plt.title(channel)
    plt.bar(histogram.xgrid, histogram.counts, width=histogram.span / histogram.nbin, label=label)
    plt.xlim([histogram.offset, histogram.offset + histogram.span])
    plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if return_fig:
        return fig

    if save:
        save_name = f'{rank}_{transformation}_{data_type}.png'
        fig.savefig(PLOT_DIR + save_name, dpi=300)
        return save_name
    else:
        plt.show(block=block)
    plt.clf()


def plot_histogram_cdf(histogram, channel, transformation, data_type, xlabel='x', ylabel='CDF', label=None, save=False, rank=None, fig=None, return_fig=False):
    label = label if label else data_type
    transformation = transformation if transformation != '' else 'none'
    f_name = f'{rank}_{channel}_{transformation}_cdf+{data_type}'
    LOG.info(f'Plotting {f_name}...')

    if not fig:
        fig = plt.figure(figsize=(10, 8))

    plt.rcParams['font.size'] = 16
    plt.plot(histogram.xgrid, histogram.cdf, label=label)
    plt.legend(loc='upper left')
    plt.title(channel)
    plt.xlim(min(histogram.xgrid), max(histogram.xgrid))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if return_fig:
        return fig

    if save:
        save_name = f'{rank}_{transformation}_{data_type}_cdf.png'
        fig.savefig(PLOT_DIR + save_name, dpi=300)
        return save_name
    else:
        plt.show()
    plt.clf()
    return None
