import cProfile

from tqdm import tqdm
from fnmatch import fnmatch

from application1.model.channel import Channel

from virgotools.frame_lib import FrameFile

source = '/virgoData/ffl/raw_O3b_arch'
t_start = 1262230000
t_stop = t_start + 100
f_target = 50

exclude_patterns = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms']
frame_file = FrameFile(source)


def get_available_channels(t0):
    with frame_file.get_frame(t0) as f:
        channels = [Channel(name=str(adc.contents.name),
                            f_sample=adc.contents.sampleRate)
                    for adc in f.iter_adc()]
        if exclude_patterns:
            return [c for c in channels if not any(fnmatch(c.name, p) for p in exclude_patterns)]
        else:
            return channels


channels = get_available_channels(t0=t_start)
print(f'number of channels: {len(channels)}')

channels = [c for c in channels if c.f_sample >= f_target]
print(f'number of channels (>=50Hz): {len(channels)}')


def test_getChannel():
    for channel in tqdm(channels):
        try:
            frame_file.getChannel(channel.name, t_start, t_stop)
        except UnicodeDecodeError:
            print(f'error trying to decode {channel}. Skipping.')


cProfile.run('test_getChannel()')
""" result
14458 channels found
3800 channels >= 50Hz

calling getChannel on every one takes 

"""
