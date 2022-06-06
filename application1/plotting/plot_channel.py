
from virgotools.frame_lib import FrameFile


source =


def plot(channel, gs, ge):
    with FrameFile(source) as ff:
        unsampled_data = ff.getChannel(channel, gs, ge).data