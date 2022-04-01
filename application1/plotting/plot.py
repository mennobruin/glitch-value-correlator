import matplotlib.pyplot as plt
from resources.constants import PLOT_DIR
from application1.config import config_manager


LOG = config_manager.get_logger(__name__)


def plot_histogram(data, save=False):
    pass


def plot_histogram(channel, transformation, histogram, data_type, save=False, score=None):
    transformation = transformation if transformation != '' else 'none'
    f_name = f'{score}_{channel}_{transformation}+{data_type}'
    LOG.info(f'Plotting {f_name}...')

    fig = plt.figure(figsize=(10, 8), dpi=100)

    plt.title(f_name)
    plt.bar(histogram.xgrid, histogram.counts, width=histogram.span / histogram.nbin)
    plt.xlim([histogram.offset, histogram.offset + histogram.span])

    if save:
        save_name = f'{score}_{transformation}_{data_type}'
        fig.savefig(PLOT_DIR + save_name + '.png', dpi=fig.dpi)
    else:
        plt.show()
    plt.clf()


def plot_histogram_cdf(histogram, channel, transformation, data_type, save=False, score=None, fig=None, return_fig=False):
    transformation = transformation if transformation != '' else 'none'
    f_name = f'{score}_{channel}_{transformation}_cdf+{data_type}'
    LOG.info(f'Plotting {f_name}...')

    if not fig:
        fig = plt.figure(figsize=(10, 8), dpi=100)

    plt.plot(histogram.xgrid, histogram.cdf, label=data_type)
    plt.legend(loc='upper left')

    if return_fig:
        return fig

    if save:
        save_name = f'{score}_{transformation}_{data_type}_cdf.png'
        fig.savefig(PLOT_DIR + save_name, dpi=fig.dpi)
        return save_name
    else:
        plt.show()
    plt.clf()
    return None
