import scipy.signal


# https://scipy-cookbook.readthedocs.io/items/ButterworthBandpass.html


def butterworth_bandpass(signal, sample_rate=44100.0, low_frequency=80.0, high_frequency=1100.0, order=5):
    nyquist_frequency = 0.5 * sample_rate  # Nyquist (folding) frequency
    numerator_coefficients, denominator_coefficients = scipy.signal.butter(order, [low_frequency / nyquist_frequency, high_frequency / nyquist_frequency], btype='bandpass')
    filtered_signal = scipy.signal.lfilter(numerator_coefficients, denominator_coefficients, signal)
    return filtered_signal
