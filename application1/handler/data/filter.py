from scipy.signal import lfilter, lfilter_zi, filtfilt, cheby1


class Filter:

    P_MAX = 5
    MAX_RATIO = 2 ** P_MAX
    FILTER_ORDER = 4
    MAX_RIPPLE = 0.05

    def __init__(self, ratio):
        self.states = None
        self.ratios = self._init_ratios(ratio)
        self.filter_coefficients: {int: object} = self._init_filter()

    def _init_filter(self):
        return dict(
                (2 ** p, cheby1(self.FILTER_ORDER, self.MAX_RIPPLE, 0.8 / 2 ** p)) for p in range(self.P_MAX)
            )

    def _init_ratios(self, ratio):
        ratios = []
        while ratio > 1:
            factor = min(ratio, self.MAX_RATIO)  # fixme: only works for powers of 2
            assert ratio % factor == 0
            ratios.append(factor)
            ratio //= factor
        return self.ratios

    def _init_states(self, x):
        self.states = [x[0] * lfilter_zi(*self.filter_coefficients[ratio]) for ratio in self.ratios]

    def filter(self, input_data, offline=False):
        if self.states is None and not offline:
            self._init_states(x=input_data)

        output_data = input_data
        for i, ratio in enumerate(self.ratios):
            b, a = self.filter_coefficients[ratio]
            if offline:
                output_data, self.states[i] = filtfilt(b, a, output_data)
            else:
                output_data, self.states[i] = lfilter(b, a, output_data, zi=self.states[i])
            output_data = output_data[::ratio]

        return output_data


if __name__ == '__main__':
    _filter = Filter()
    _filter.filter([])
    print(_filter.filter_coefficients)
