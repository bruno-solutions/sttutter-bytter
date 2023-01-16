import re
from math import copysign
from typing import Union

import pydub

from configuration import Configuration
from logger import Logger


def to_hertz(value: Union[str, float, int]) -> float:
    """
    Converts a string, float, or integer value to decibels (untested)

    - numeric values are treated as hertz (requiring no conversion) e.g., -21.1 or 5
    - string values ending with '', 'hz', or 'hertz' are treated as hertz, e.g., '88.8', '440hz', '1500 hertz'

    Args:
    :param value:  hertz value as a string, float, or integer value
    """
    if isinstance(value, int) or isinstance(value, float):
        return value

    note: str = "Hertz are positive numeric values, or strings ending with one of the following units: '', 'hz', 'hertz'"

    if not isinstance(value, str):
        Logger.warning(f"Hertz value argument type not valid {value} of {type(value)} [Fixup: returning 440 hertz]")
        Logger.warning(note)
        return 440

    string: str = value.replace(' ', '')

    if '' == string:
        return 440

    parts: [str] = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number: float = float(parts[1])
    units: str = parts[2]

    if 0 > number:
        number = -number
        Logger.warning(f"Hertz value negative, {string} [Fixup: returning {number} hertz]")
        Logger.warning(note)

    if '' == units or 'hz' == units or 'hertz' == units:
        return number

    Logger.warning(f"Hertz argument units invalid, {string} [Fixup: returning {number} hertz]")
    Logger.warning(note)

    return number


def to_decibels(value: Union[str, float, int]) -> float:
    """
    Converts a string, float, or integer value to decibels (untested)

    - numeric values are treated as decibels (requiring no conversion) e.g., -21.1 or 5
    - string values ending with '', 'db', 'dbs', or 'decibels' are treated as decibels, e.g., '3.1', '-20db', '.15 decibels'

    Args:
    :param value:  decibel as a string, float, or integer value
    """
    if isinstance(value, int) or isinstance(value, float):
        return value

    note: str = "Decibels are numeric values, or strings ending with one of the following units: '', 'db', 'dbs', 'decibels'"

    if not isinstance(value, str):
        Logger.warning(f"Decibel level argument type not valid {value} of {type(value)} [Fixup: returning 0 decibels]")
        Logger.warning(note)
        return 0.0

    string: str = value.replace(' ', '')

    if '' == string:
        return 0.0

    parts: [str] = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number: float = float(parts[1])
    units: str = parts[2]

    if '' == units or 'db' == units or 'dbs' == units or 'decibels' == units:
        return number

    Logger.warning(f"Decibel level argument units invalid, {string} [Fixup: returning {number} decibels]")
    Logger.warning(note)

    return number


def milliseconds_to_index(milliseconds, segment: pydub.AudioSegment):
    """
    Converts milliseconds to a sample index within the audio segment (untested)
    Args:
    :param milliseconds: a point within the audio segment in milliseconds
    :param segment:     a segment of an audio recording
    """
    frames_per_millisecond = segment.frame_rate / 1000
    maximum_milliseconds = Configuration().get('maximum_samples') * (segment.frame_rate / 1000)

    if maximum_milliseconds < abs(milliseconds):
        maximum_milliseconds = copysign(Configuration().get('maximum_samples'), maximum_milliseconds)
        Logger.warning(f"Number of milliseconds too large {milliseconds} [Fixup: using {maximum_milliseconds}]")
        milliseconds = maximum_milliseconds

    return milliseconds * frames_per_millisecond


def index_to_milliseconds(index: int, segment: pydub.AudioSegment) -> float:
    """
    Converts a sample index to milliseconds within the audio segment (untested)
    Args:
    :param index:   a sample index within the audio segment
    :param segment: a segment of an audio recording
    """
    frames_per_millisecond: float = segment.frame_rate / 1000

    if Configuration().get('maximum_samples') < abs(index):
        maximum_index: int = int(copysign(Configuration().get('maximum_samples'), index))
        Logger.warning(f"Sample index magnitude too large {index} [Fixup: using {maximum_index}]")
        index = maximum_index

    return index / frames_per_millisecond


def to_milliseconds(value: Union[str, float, int], segment_milliseconds: int) -> int:
    """
    Converts a string, float, or integer value to milliseconds

    - numeric values over 1 are treated as milliseconds (requiring no conversion) e.g., 1.1 or 123456
    - numeric values between 0.0 and 1.0 are treated as decimal percentage of the segment length, e.g., 0.5275
    - string values ending with '%' are treated as a percentage of the segment length, e.g., '99.99%'
    - string values ending with 's', 'sec', 'secs', or 'seconds' are treated as seconds, e.g., '27s', '250 sec', or '9.3 seconds'
    - string values ending with '', 'ms', or 'milliseconds' are treated as milliseconds, e.g., '33750', '5960444.8ms', '7600000000 milliseconds'

    Args:
    :param value:               duration as a percent of the audio segment, number of seconds, or number of milliseconds as a string, float, or integer value
    :param segment_milliseconds: the length of the audio segment to use to calculate a milliseconds percentage values (optional)
    """
    if isinstance(value, int) or isinstance(value, float):
        return int(segment_milliseconds * value if 0 <= value <= 1 else value)  # decimal percentage of the segment or already milliseconds

    note: str = "Durations are numeric values, or strings ending with one of the following units: 's', 'sec', 'secs', 'seconds', 'ms', 'milliseconds', or '%'"

    if not isinstance(value, str):
        Logger.warning(f"Duration argument type not valid {value} of {type(value)} [Fixup: returning 0]")
        Logger.warning(note)
        return 0

    string: str = value.replace(' ', '')

    if '' == string:
        return 0

    parts: [str] = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number: float = float(parts[1])
    units: str = parts[2]

    try:
        if '' == units and 0 <= number <= 1:  # floating point percentage e.g., 0.5275
            return int(segment_milliseconds * number)
        if '%' == units:  # string percentage e.g., '99.99%'
            return int(segment_milliseconds * number / 100)
    except TypeError:
        Logger.error("When expressing a duration as a percentage an audio segment length (in milliseconds) is required")
        return 0

    if 's' == units or 'sec' == units or 'secs' == units or 'seconds' == units:
        return int(number * 1000)
    if '' == units or 'ms' == units or 'milliseconds' == units:
        return int(number)

    Logger.warning(f"Duration argument units invalid, {string} [Fixup: treating as {number} milliseconds]")
    Logger.warning(note)

    return int(number)


def parse_common_arguments(arguments: {}, recording: pydub.AudioSegment) -> (int, pydub.AudioSegment, int, int, int):
    """
    Extracts common slicer processing arguments
    Args:
    :param arguments: slicer arguments from which common ones will be parsed, validated, and returned
    :param recording: the downloaded audio recording to be sliced
    """
    recording_ms: int = len(recording)

    weight: int = int(arguments['weight']) if 'weight' in arguments else 1
    begin: int = to_milliseconds(arguments['begin'], recording_ms) if 'begin' in arguments else 0
    end: int = to_milliseconds(arguments['end'], recording_ms) if 'end' in arguments else recording_ms
    clip_size: int = to_milliseconds(arguments['clip_size'], recording_ms) if 'clip_size' in arguments else Configuration().get('clip_size_milliseconds')
    clips: int = arguments['clips'] if 'clips' in arguments else Configuration().get('clips_per_stage')

    note = "Note: use values between 0.0 and 1.0 ('100%') to calculate a percentage of the clip duration as the starting or stopping point for clip generation"

    if 0 > begin:
        Logger.warning(f"Argument 'begin' {begin} invalid, must be between 0 and the recording length in milliseconds {recording_ms} [Fixup: using 0 ms]")
        Logger.warning(f"Omit or set the 'begin' argument to 0 to start at the first sample of the recording")
        begin = 0
        if note is not None:
            Logger.warning(note)
            note = None
    if recording_ms < begin:
        Logger.warning(f"Argument 'end' {begin} invalid, must be between 0 and the recording length in milliseconds {recording_ms} [Fixup: using {recording_ms} ms]")
        begin = recording_ms
        if note is not None:
            Logger.warning(note)
            note = None
    if 0 > end:
        Logger.warning(f"Argument 'end' {end} invalid, must be between 0 and the recording length in milliseconds {recording_ms} [Fixup: using 0 ms]")
        end = 0
        if note is not None:
            Logger.warning(note)
            note = None
    if recording_ms < end:
        Logger.warning(f"Argument 'end' {end} invalid must, be between 0 and the recording length in milliseconds {recording_ms} [Fixup: using {recording_ms} ms]")
        Logger.warning(f"Omit or set the 'end' argument to 1 to stop at the last sample of the recording")
        end = recording_ms
        if note is not None:
            Logger.warning(note)
            note = None
    if begin > end:
        begin, end = end, begin
        Logger.warning(f"Argument begin {end} and end {begin} were reversed [Fixup: using {begin},{end}]")

    if note is not None:
        Logger.debug(note)

    if 0 > weight:
        weight = 0

    return weight, recording[begin:end], milliseconds_to_index(begin, recording), clip_size, clips
