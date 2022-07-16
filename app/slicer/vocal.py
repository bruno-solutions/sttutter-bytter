from typing import List

import numpy
import pydub.effects
from spleeter.separator import Separator

from configuration import LOG_DEBUG, TEMP_VOCAL_FILE_NAME, AUDIO_FILE_TYPE
from logger import Logger
from normalizer import Normalizer
from sample_clipping_interval import SampleClippingInterval
from volume import VolumeSlicer

models = ['spleeter:2stems', 'spleeter:4stems', 'spleeter:5stems', 'spleeter:2stems-16kHz', 'spleeter:4stems-16kHz', 'spleeter:5stems-16kHz']


class VocalSlicer:
    """
    Slice source audio recording using vocal cues
    """

    def __init__(self, recording: pydub.AudioSegment, stage: int, passes: int, model, detection_chunk_size_miliseconds: int, low_volume_threshold_decibels: int, volume_drift_decibels: int, max_clips: int, logger: Logger):
        """
        Args:
        :param recording:                        an audio segment object that contains the audio samples to be processed
        :param stage:                            the stage within the series of slicers that the vocal slicer is being executed
        :param model:                            indicates which Spleeter traing model to use for vocal separation
        :param detection_chunk_size_miliseconds: the number of samples of the recording to analyze per chunk
        :param low_volume_threshold_decibels:    the minimum decible value to use when determining the peak volume of a chunk
        :param volume_drift_decibels:            the maximum decibles that the peak amplitude can be increased by a sample (limits the effect of spikes)
        :param max_clips:                        create no more than this many clips from the recording
        :param logger:                           sends error, warning, and debug messages to a log file and/or the console
        """
        try:
            if isinstance(model, int):
                if 0 >= model and model < len(models):
                    model = models[model]
                else:
                    logger.warning(f"Invalid model index [{model}] provided, defaulting to index [0]")
                    raise IndexError
            elif model is None or model not in models:
                logger.warning(f"Invalid model '{model}' provided, defaulting to '{models[0]}'")
                raise ValueError
        except IndexError or ValueError:
            logger.warning(f"The available Spleeter training models are: [0]'{models[0]}' [1]'{models[1]}' [2]'{models[2]} [3]'{models[3]}' [4]'{models[4]}' [5]'{models[5]}'")
            model = models[0]

        # TODO Consider wav subtraction of other models

        # https://github.com/deezer/spleeter

        logger.debug(f"Slicing stage[{stage}], Vocal Slicer using Spleeter training model '{model}'")

        for iteration in range(passes):
            logger.debug(f"Vocal slicer Spleeter pass [{iteration + 1} of {passes}] starting")
            logger.characteristics(recording, f"Recording characteristics")

            samples = recording.get_array_of_samples()  # [19,535,872] (int16) = 39,071,744 bytes
            samples_reshaped = numpy.reshape(samples, (-1, recording.channels))  # [9,767,936 (int16), 2] = 19,535,872 (int) = 39,071,744 bytes
            vocals = Separator(model, multiprocess=False).separate(samples_reshaped)['vocals']  # [9,767,936 (float), 2] = 19,535,872 (float) = 78,143,488 bytes
            vocals_as_int = numpy.array(vocals, dtype=numpy.int16)  # [9,767,936 (int16), 2] = 19,535,872 (int) = 39,071,744 bytes
            vocals_as_int_reshaped = numpy.reshape(vocals_as_int, (recording.channels, -1))  # [2, 9,767,936 (int16)] = 19,535,872 (int16) = 39,071,744 bytes
            as_bytes = vocals_as_int_reshaped.tobytes()  # [39,071,744] bytes
            vocal_recording = pydub.AudioSegment(data=as_bytes, frame_rate=recording.frame_rate, sample_width=recording.sample_width, channels=recording.channels)
            vocal_recording = Normalizer.stereo_normalization(pydub.effects.high_pass_filter(pydub.effects.low_pass_filter(pydub.effects.compress_dynamic_range(vocal_recording, attack=1, release=1), cutoff=70), cutoff=200))

            if LOG_DEBUG:
                vocal_recording.export(out_f=f"{TEMP_VOCAL_FILE_NAME}.{model.replace(':', '.')}.stage.{stage}.pass.{iteration + 1}.{AUDIO_FILE_TYPE}", format=AUDIO_FILE_TYPE).close()

            recording = vocal_recording

        logger.characteristics(recording, f"Vocal slicer post {passes} pass Spleeter processing recording characteristics")

        volume_slicer = VolumeSlicer(recording, stage, detection_chunk_size_miliseconds, low_volume_threshold_decibels, volume_drift_decibels, max_clips)

        self.sci: List[SampleClippingInterval] = volume_slicer.get()

    def get(self):
        return self.sci
