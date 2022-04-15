import numpy as np
import matplotlib.pyplot as plt
from resources.constants import RESOURCE_DIR
from application1.handler.triggers import DefaultPipeline

file = RESOURCE_DIR + 'csv/GSpy_ALLIFO_O3b_0921_final.csv'


def plot_trigger_density(trigger):
    pipeline = DefaultPipeline(trigger_file=file, trigger_type=trigger)
    triggers = pipeline.get_segment(gps_start=1265997618, gps_end=1266037218)
    # triggers = pipeline.triggers
    print(f'{triggers.size} triggers found')
    plt.hist(triggers, bins=100)
    plt.show()


plot_trigger_density(trigger='Scattered_Light')
