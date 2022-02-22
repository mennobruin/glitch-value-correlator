import matplotlib.pyplot as plt
import h5py
import pathlib
import os


resource_path = str(pathlib.Path(__file__).parents[1].resolve()) + '/application1/resources/'
ds_path = resource_path + 'ds_data/'
data_path = ds_path + 'data/'

files = os.listdir(data_path)
for f in files:
    hfile = h5py.File(data_path + f, 'r')
    data = hfile.keys()
    print(data[0:10])
