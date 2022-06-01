import pickle

from .plot import plot_histogram
from application1.model.transformation import HighPass, GaussianDifferentiator

transformation_combinations = [
    [],
    [GaussianDifferentiator],
    [HighPass]
]

join_names = lambda c: '_'.join(t.NAME for t in c)
transformation_names = [join_names(t) for t in transformation_combinations]

t_start = 1256688000
t_stop = 1256774400

test_file = f'test_{t_start}_{t_stop}.pickle'
with open(test_file, 'rb') as pkf:
    data = pickle.load(pkf)
    h_trig_cum = data['trig']
    h_aux_cum = data['aux']
    available_channels = data['channels']


# print([c for c in available_channels if "DQ" in c])
# channel = "V1:DQ_BRMSMon_BRMS_ALL_MIC_AIRPLANE_ENV_TCS_CO2_WI_MIC"
# i = available_channels.index(channel)
i = 2
channel = available_channels[i]
transformation = transformation_names[0]
plot_histogram(channel=channel, transformation=transformation, histogram=h_trig_cum[channel, transformation], data_type='trig', block=False)
plot_histogram(channel=channel, transformation=transformation, histogram=h_aux_cum[channel, transformation], data_type='aux', block=False)

transformation = transformation_names[2]
plot_histogram(channel=channel, transformation=transformation, histogram=h_trig_cum[channel, transformation], data_type='trig', block=False)
plot_histogram(channel=channel, transformation=transformation, histogram=h_aux_cum[channel, transformation], data_type='aux', block=False)
