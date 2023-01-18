from typing import Final

import librosa
import numpy
import soundfile as sound_file

from audioprocessor.filter import butterworth_bandpass

COMPONENTS: Final = 8


# https://github.com/source-separation/tutorial/tree/master/common
# https://librosa.org/librosa_gallery/auto_examples/plot_vocal_separation.html

def decompose(uri: str):
    samples, sample_rate = librosa.load(uri, duration=120)
    sound_file.write('original.wav', samples, sample_rate)

    # orders = [5, 6]
    # frequencies = [80.0, 120.0, 180.0, 260.0, 360.0, 480.0, 620.0, 780.0, 960.0, 1160.00]

    orders = [7]
    frequencies = [90.0, 180.0, 360.0, 720.0, 1440.00]

    for order in orders:
        for low in frequencies:
            for high in frequencies:
                if low < high:
                    filtered_data = butterworth_bandpass(samples, sample_rate=sample_rate, low_frequency=low, high_frequency=high, order=order)
                    if not numpy.all(numpy.isfinite(filtered_data)):
                        print("no samples when filtering: " + str(low) + ' hz, ' + str(high) + ' hz, ' + str(order) + ' order')
                    else:
                        filtered_data = librosa.util.normalize(filtered_data)
                        sound_file.write(str(low) + 'hz.' + str(high) + 'hz.' + str(order) + '.filtered.wav', filtered_data, sample_rate)

                        spectrogram = librosa.stft(filtered_data)
                        magnitude, phase = librosa.magphase(spectrogram)
                        spectrogram_filter = librosa.decompose.nn_filter(magnitude, aggregate=numpy.median, metric='cosine', width=int(librosa.time_to_frames(2, sr=sample_rate)))
                        spectrogram_filter = numpy.minimum(magnitude, spectrogram_filter)

                        margin_i, margin_v, power = 2, 10, 2

                        mask_i = librosa.util.softmask(spectrogram_filter, margin_i * (magnitude - spectrogram_filter), power=power)
                        s_background = mask_i * magnitude
                        s_background_data = librosa.util.normalize(librosa.istft(s_background * numpy.exp(1j * numpy.angle(spectrogram))))
                        sound_file.write(str(low) + 'hz.' + str(high) + 'hz.' + str(order) + '.background.wav', s_background_data, sample_rate)

                        mask_v = librosa.util.softmask(magnitude - spectrogram_filter, margin_v * spectrogram_filter, power=power)
                        s_foreground = mask_v * magnitude
                        s_foreground_data = librosa.util.normalize(librosa.istft(s_foreground * numpy.exp(1j * numpy.angle(spectrogram))))
                        sound_file.write(str(low) + 'hz.' + str(high) + 'hz.' + str(order) + '.foreground.wav', s_foreground_data, sample_rate)

                        s_foreground_data = butterworth_bandpass(s_foreground_data, sample_rate=sample_rate)
                        if numpy.all(numpy.isfinite(s_foreground_data)):
                            s_foreground_data = librosa.util.normalize(s_foreground_data)
                            sound_file.write(str(low) + 'hz.' + str(high) + 'hz.' + str(order) + '.foreground.filtered.wav', s_foreground_data, sample_rate)


def decompose1(uri: str):
    audio_time_series, sampling_rate = sound_file.read(uri)
    rotated_audio_time_series = numpy.reshape(audio_time_series, (2, -1))
    mono_audio_time_series = librosa.to_mono(rotated_audio_time_series)
    spectrogram_time_series = librosa.stft(mono_audio_time_series)
    magnitude_time_series, phase_time_series = librosa.magphase(spectrogram_time_series)
    # scaled_magnitude_time_series = numpy.absolute(magnitude_time_series)

    # Separate the vocals and instrumentals using NMF
    components, activations = librosa.decompose.decompose(magnitude_time_series, n_components=COMPONENTS, sort=True, fit=True)

    for index in range(COMPONENTS):
        component = librosa.istft(numpy.outer(components[:, index], activations[index]) * numpy.exp(1j * numpy.angle(spectrogram_time_series)))
        sound_file.write('component.' + str(index) + '.wav', component, sampling_rate)
