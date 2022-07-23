from typing import List

import numpy
import pydub.effects
from numpy import ndarray
from spleeter.separator import Separator

from arguments import parse_common_arguments
from configuration import LOG_DEBUG, OUTPUT_FILE_TYPE, TEMP_ROOT
from logger import Logger
from sci import SampleClippingInterval
from volume import VolumeSlicer

models = ['spleeter:2stems', 'spleeter:4stems', 'spleeter:5stems', 'spleeter:2stems-16kHz', 'spleeter:4stems-16kHz', 'spleeter:5stems-16kHz']


class VocalSlicer:
    """
    Slice source audio recording using vocal cues
    """

    def __init__(self, stage: int, arguments: {}, recording: pydub.AudioSegment, logger: Logger):
        """
        Creates a list of potential clip begin and end sample indexes using utterance onset and cessation events
        Args:
        :param stage:     the number of the method step in the slicing process
        :param arguments: the common and slicer specific operational parameters
        :param recording: the downloaded audio recording from which clips will be sliced
        :param logger:    the Logger instantiated by the main Slicer class
        """
        segment, segment_offset_index, clip_size, clips = parse_common_arguments(arguments, recording, logger)
        passes: int = arguments['passes'] if 'passes' in arguments else 1
        model: str = arguments['model'] if 'model' in arguments else 0

        # No need to extract arguments that are only used by VolumeSlicer()

        logger.debug(f"Slicing stage[{stage}], Vocal Slicer: {clips} clips using Spleeter training model '{model}'", separator=True)

        logger.debug(f"Downloaded Audio Segment Offset: {segment_offset_index}")
        logger.debug(f"Target Clip Length Miliseconds: {clip_size}")

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

        def instrument_to_segment(_recording: pydub.AudioSegment, _instruments: {}, name: str):  # [10,000,000 (float), 2] = 20,000,000 (float) = 80,000,000 bytes
            as_int: ndarray = numpy.array(_instruments[name], dtype=numpy.int16)  # [10,000,000 (int16), 2] = 20,000,000 (int) = 40,000,000 bytes
            as_int_reshaped: ndarray = numpy.reshape(as_int, (_recording.channels, -1))  # [2, 10,000,000 (int16)] = 20,000,000 (int16) = 40,000,000 bytes
            as_bytes: bytes = as_int_reshaped.tobytes()  # [40,000,000] bytes
            _segment: pydub.AudioSegment = pydub.AudioSegment(data=as_bytes, frame_rate=_recording.frame_rate, sample_width=_recording.sample_width, channels=_recording.channels)

            if LOG_DEBUG:
                _segment.export(out_f=f"{TEMP_ROOT}\\{name}.{model.replace(':', '.')}.stage.{stage}.pass.{iteration + 1}.{OUTPUT_FILE_TYPE}", format=OUTPUT_FILE_TYPE).close()

            return _segment

        # https://github.com/deezer/spleeter
        # https://github.com/audacity/audacity/blob/master/plug-ins/vocalrediso.ny

        for iteration in range(passes):
            logger.debug(f"Vocal slicer Spleeter pass [{iteration + 1} of {passes}] starting")
            logger.properties(segment, f"Recording characteristics")

            samples: ndarray = segment.get_array_of_samples()  # [20,000,000] (int16) = 40,000,000 bytes
            samples_reshaped: ndarray = numpy.reshape(samples, (-1, segment.channels))  # [10,000,000 (int16), 2] = 20,000,000 (int16) = 40,000,000 bytes
            instruments: {} = Separator(model, multiprocess=False).separate(samples_reshaped)

            vocals: pydub.AudioSegment = instrument_to_segment(recording, instruments, 'vocals')
            # drums: pydub.AudioSegment = instrument_to_segment(recording, instruments, 'drums')
            # bass: pydub.AudioSegment = instrument_to_segment(recording, instruments, 'bass')
            # piano: pydub.AudioSegment = instrument_to_segment(recording, instruments, 'piano')
            # other: pydub.AudioSegment = instrument_to_segment(recording, instruments, 'other')
            # accompaniment: pydub.AudioSegment = instrument_to_segment(recording, instruments, 'accompaniment')

            # vocals: pydub.AudioSegment = Normalizer.stereo_normalization(pydub.effects.high_pass_filter(pydub.effects.low_pass_filter(pydub.effects.compress_dynamic_range(vocals, attack=1, release=1), cutoff=70), cutoff=200))

            segment = vocals

        logger.properties(segment, f"Vocal slicer post {passes} pass Spleeter processing recording characteristics")

        self.sci: List[SampleClippingInterval] = VolumeSlicer(stage, arguments, segment, logger).get()

    def get(self):
        return self.sci
