"""
Slicer module
"""
from __future__ import annotations

from typing import List, Optional

import pydub

from beat import BeatSlicer
from chaos import ChaosSlicer
from clip import Clip
from interval import SimpleIntervalSlicer
from logger import Logger
from onset import OnsetSlicer
from pitch import PitchSlicer
from sci import SampleClippingInterval
from tempo import TempoSlicer
from .vocal import VocalSlicer
from .volume import VolumeSlicer


class Slicer:
    """
    Builds a list of weighted sample clipping intervals based upon the results of the invoked slicing methods
    from which lists of auido array sample arrays (known as clips) are prepared from a source audio recording
    """

    def __init__(self, logger: Logger = None):
        """
        Instantiate the Slicer class
        Args:
        :param logger: class to send debug, warning, and error messages to the console and log file
        """
        self.logger: Logger = logger if logger is not None else Logger()

        self.recording: Optional[pydub.AudioSegment] = None
        self.sci: List[SampleClippingInterval] = []

    def slice(self, recording: pydub.AudioSegment = None, logic: [{}] = None, sci: List[SampleClippingInterval] = None) -> Slicer:
        """
        Apply slicer methods to build a set of recording sample clipping intervals
        Args:
        :param recording: the audio recording to be sliced
        :param logic:     the slicers to use to slice the recording and the slicer arguments
        :param sci:       starter sample clipping intervals
        """
        if recording is None or 1000 > len(recording):  # refuse to slice recordings shorter than 1 second (for no particular reason)
            raise RuntimeError("Recording not provided, use the Loader class to load a file to slice")
        if logic is None or 0 == len(logic):
            raise RuntimeError("Slicer methods not declared, create a method dictionary that describes how to process and slice the recording")

        self.recording = recording
        self.sci = [] if sci is None else sci

        self.logger.debug("Slicing sample clipping intervals from the recording")

        for stage, slicer in enumerate(logic):  # execution each slicer is a "stage" in the processing of the source
            if 'active' in slicer and not slicer['active']:  # skip methods that are deactivated
                continue

            try:
                method_name = slicer['method']
            except AttributeError:
                self.logger.warning(f"Attribute 'method' not defined on slicer[{stage}]")
                self.logger.warning(f"Available methods are: 'slice_on_beat', 'slice_at_random', 'slice_on_vocal_change', 'slice_on_volume_change'")
                continue

            try:
                method = getattr(Slicer, method_name)
            except AttributeError:
                self.logger.warning(f"No slicer method named '{method_name}' is avaialable in the slicer module, referenced in slicer[{stage}]")
                self.logger.warning(f"Available methods are: 'slice_on_beat', 'slice_at_random', 'slice_on_vocal_change', 'slice_on_volume_change'")
                continue

            try:
                arguments = slicer['arguments']
            except KeyError:
                self.logger.debug(f"'arguments' not provided for '{method_name}', using default values")
                arguments = {}

            self.logger.properties(recording, f"Pre-stage:{stage} [{method_name}] slicing recording characteristics")
            method(self, stage, arguments)  # -> None
            self.logger.properties(recording, f"Post-stage:{stage} [{method_name}] slicing recording characteristics")

        self.logger.debug(f"Sliced {len(self.sci)} sample clipping intervals from the recording")
        return self

    def get(self, start: int = None, length: int = None) -> [Clip]:
        """
        Generate audio segment clips from the recording based upon the sample clipping intervals determined by slice()
        Args:
        :param start:  the index of the first clip to return (to support pagination/memory management)
        :param length: the maximum number of clips to return (to support pagination/memory management)
        """
        start = 0 if start is None else start
        length = len(self.sci) if length is None else length

        self.logger.properties(self.recording, "Clip creation recording characteristics")

        # TODO add logic to evaluate clips by combined weighting of the clipping methods used

        clips: [Clip] = [Clip]
        finish: int = min(start + length, len(self.sci)) - 1
        for index in range(start, finish):
            clips.append(Clip(self.recording, self.sci[index]))
        return clips

    def slice_on_beat(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on the musical every beat slicer:
        Identifies single beats and groups these into consecutive ranges in overlapping multiples of the requested beat count
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += BeatSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_at_interval(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice equally spaced clips slicer:
        Processes based upon the clip size slicer, the desired number of clips, and the duration of the downloaded audio recording
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += SimpleIntervalSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_at_random(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice randomly slicer:
        Adds noise to the clip weightings for statistical balancing
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += ChaosSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_on_vocal_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on vocal cues slicer:
        Processes by filtering vocal and then performing volume change detection
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += VocalSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_on_volume_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on volume change slicer:
        Processes by measuring volume fluctuations in 'detection_window' sized chunks of the recording
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += VolumeSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_at_onset(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on onset detection slicer:
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += OnsetSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_on_tempo_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on tempo change detection slicer:
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += TempoSlicer(stage, arguments, self.recording, self.logger).get()

    def slice_on_pitch_change(self, stage: int, arguments: {}) -> None:
        """
        Wrapper for the slice on pitch change detection slicer:
        Args:
        :param stage:     the index of the slicing method being processed
        :param arguments: a dictionary of the common and slicing method specific processing parameters
        """
        self.sci += PitchSlicer(stage, arguments, self.recording, self.logger).get()

    @staticmethod
    def get_slicer_methods() -> list[str]:
        """
        Returns a list of the available slicer methods to assist users in writing slicing scripts:
        Note: all slicer wrapper method names must begin with "slice_"
        """
        return [attribute for attribute in dir(Slicer) if attribute.startswith("slice_") and callable(getattr(Slicer, attribute))]
