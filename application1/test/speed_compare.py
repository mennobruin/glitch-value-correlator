import cProfile

from tqdm import tqdm
from fnmatch import fnmatch

from application1.model.channel import Channel

import PyFd as fd
from virgotools.frame_lib import FrameFile, FrVect2array


source = '/virgoData/ffl/raw_O3b_arch.ffl'
t_start = 1262230000
t_stop = t_start + 1000
f_target = 50

exclude_patterns = ['*max', '*min', 'V1:VAC*', 'V1:Daq*', '*rms']


def get_available_channels(t0):
    ff = FrameFile(source)
    with ff.get_frame(t0) as f:
        channels = [Channel(name=str(adc.contents.name),
                            f_sample=adc.contents.sampleRate)
                    for adc in f.iter_adc()]
        if exclude_patterns:
            return [c for c in channels if not any(fnmatch(c.name, p) for p in exclude_patterns)]
        else:
            return channels


# channels = get_available_channels(t0=t_start)
# print(f'number of channels: {len(channels)}')
#
# channels = [c for c in channels if c.f_sample >= f_target]
# print(f'number of channels (>=50Hz): {len(channels)}')
#
#
ff = FrameFile(source)
# def test_getChannel():
#     for channel in tqdm(channels):
#         try:
#             ff.getChannel(channel.name, t_start, t_stop)
#         except UnicodeDecodeError:
#             print(f'error trying to decode {channel.name}. Skipping.')


def test_iterAdc():
    dt = 10
    for t in tqdm(range(t_start, t_stop, dt)):
        with ff.get_frame(t) as f:
            for adc in f.iter_adc():
                f_sample = adc.contents.sampleRate
                if f_sample >= 50:
                    data = FrVect2array(adc.contents.data)


ff2 = fd.FrFileINew(source)
for frame in ff2:
    print(frame.contents.__dict__)
    break


def test_diy():
    dt = 10
    for t in tqdm(range(t_start, t_stop, dt)):
        frame = fd.FrameReadT(ff2, t)
        try:
            adc = frame.contents.rawData.contents.firstAdc
            while adc:
                f_sample = adc.contents.sampleRate
                if f_sample >= 50:
                    data = FrVect2array(adc.contents.data)
                adc = adc.contents.next
        except Exception as e:
            print(f"exception caught: {e}")
        finally:
            fd.FrameFree(frame)


# test_iterAdc()
# test_diy()

# cProfile.run('test_iterAdc()')
""" results
14458 channels found
3800 channels >= 50Hz

calling getChannel on every one takes 14m00s, of which 13m29s come from getChannel
using get_frame + iter_adc takes 2m36s / 2m41, of which 2m13 / 2m16 come from get_frame (*)
using PyFd directly takes 2m23s / 2m32s (*)
(*) n.b: includes loading frame file, which is slow, picks up speed.

pre-loading frame file:
using get_frame + iter_adc takes 2m24s / 2m16 / 2m16 / 2m22
using PyFd directly takes 2m21s / 2m09s / 2m28 / 2m18

using PyFd directly on 1000s of data takes 18m26s, which is 1.1x realtime

"""
