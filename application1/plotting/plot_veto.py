import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

from application1.handler.data.reader.h5 import H5Reader
from application1.handler.triggers import DefaultPipeline
from application1.model.fom import KolgomorovSmirnov, AndersonDarling
from application1.model.transformation import HighPass, GaussianDifferentiator
from application1.utils import slice_triggers_in_segment, config_manager

plt.rcParams['font.size'] = 16
RESULTS_DIR = 'results/'
f_target = 50

transformation_combinations = [
    [],
    [GaussianDifferentiator],
    [HighPass]
]

join_names = lambda c: '_'.join(t.NAME for t in c)
transformation_names = [join_names(t) for t in transformation_combinations]
config = config_manager.load_config()
with open(config['project.blacklist_patterns'], 'r') as blf:
    bl_patterns: list = blf.read().splitlines()
t_start = config['project.start_time']
t_stop = config['project.end_time']
h5_reader = H5Reader(gps_start=t_start, gps_end=t_stop, exclude_patterns=bl_patterns)
available_channels = h5_reader.get_available_channels()


def plot_trigger_hist():
    test_file = f'test_{t_start}_{t_stop}.pickle'
    fom_file = f'fom_{t_start}_{t_stop}.pickle'
    if os.path.exists(test_file):
        with open(test_file, 'rb') as pkf:
            data = pickle.load(pkf)
            h_trig_cum = data['trig']
            h_aux_cum = data['aux']

        if not os.path.exists(fom_file):
            fom_ks = KolgomorovSmirnov()
            fom_ad = AndersonDarling()
            for channel in available_channels:
                for transformation_name in transformation_names:
                    h_aux = h_aux_cum[channel, transformation_name]
                    h_trig = h_trig_cum[channel, transformation_name]
                    h_aux.align(h_trig)

                    fom_ks.calculate(channel, transformation_name, h_aux, h_trig)
                    fom_ad.calculate(channel, transformation_name, h_aux, h_trig)

            with open(fom_file, 'wb') as pkf:
                pickle.dump({'ks': fom_ks, 'ad': fom_ad}, pkf)
        else:
            with open(fom_file, 'rb') as pkf:
                data = pickle.load(pkf)
                fom_ks = data['ks']
                fom_ad = data['ad']

        ks_results = sorted(fom_ks.scores.items(), key=lambda f: f[1].d_n, reverse=True)
        ad_results = sorted(fom_ad.scores.items(), key=lambda f: f[1].ad, reverse=True)
        winner = ad_results[0]
        print(winner)
    else:
        print(f'{test_file=} not found, check t_start/t_stop in config.yaml')


plot_trigger_hist()
