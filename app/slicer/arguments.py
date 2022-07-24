import re
from math import copysign
from typing import Union

import pydub

from configuration import DEFAULT_CLIP_SIZE_MILISECONDS, DEFAULT_CLIPS_PER_STAGE, MAXIMUM_SAMPLES
from logger import Logger


def to_hertz(value: Union[str, float, int], logger: Logger) -> float:
    """
    Converts a string, float, or integer value to decibels (untested)

    - numeric values are treated as hertz (requiring no conversion) e.g., -21.1 or 5
    - string values ending with '', 'hz', or 'hertz' are treated as hertz, e.g., '88.8', '440hz', '1500 hertz'

    Args:
    :param value:  hertz value as a string, float, or integer value
    :param logger: a Logger class to use to record warning and/or debug information
    """
    if isinstance(value, int) or isinstance(value, float):
        return value

    note: str = "Hertz are positive numeric values, or strings ending with one of the following units: '', 'hz', 'hertz'"

    if not isinstance(value, str):
        logger.warning(f"Hertz value argument type not valid {value} of {type(value)} [Fixup: returning 440 hertz]")
        logger.warning(note)
        return 440

    string: str = value.replace(' ', '')

    if '' == string:
        return 440

    parts: [str] = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number: float = float(parts[1])
    units: str = parts[2]

    if 0 > number:
        number = -number
        logger.warning(f"Hertz value negative, {string} [Fixup: returning {number} hertz]")
        logger.warning(note)

    if '' == units or 'hz' == units or 'hertz' == units:
        return number

    logger.warning(f"Hertz argument units invalid, {string} [Fixup: returning {number} hertz]")
    logger.warning(note)

    return number


def to_decibels(value: Union[str, float, int], logger: Logger) -> float:
    """
    Converts a string, float, or integer value to decibels (untested)

    - numeric values are treated as decibels (requiring no conversion) e.g., -21.1 or 5
    - string values ending with '', 'db', 'dbs', or 'decibles' are treated as decibels, e.g., '3.1', '-20db', '.15 decibels'

    Args:
    :param value:  decibel as a string, float, or integer value
    :param logger: a Logger class to use to record warning and/or debug information
    """
    if isinstance(value, int) or isinstance(value, float):
        return value

    note: str = "Decibles are numeric values, or strings ending with one of the following units: '', 'db', 'dbs', 'decibels'"

    if not isinstance(value, str):
        logger.warning(f"Decibel level argument type not valid {value} of {type(value)} [Fixup: returning 0 decibels]")
        logger.warning(note)
        return 0.0

    string: str = value.replace(' ', '')

    if '' == string:
        return 0.0

    parts: [str] = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number: float = float(parts[1])
    units: str = parts[2]

    if '' == units or 'db' == units or 'dbs' == units or 'decibels' == units:
        return number

    logger.warning(f"Decibel level argument units invalid, {string} [Fixup: returning {number} decibels]")
    logger.warning(note)

    return number


def miliseconds_to_index(miliseconds, segment: pydub.AudioSegment, logger: Logger):
    """
    Converts miliseconds to a sample index within the audio segment (untested)
    Args:
    :param miliseconds: a point within the audio segment in miliseconds
    :param segment:     a segment of an aduio recording
    :param logger:      a Logger class to use to record warning and/or debug information
    """
    frames_per_milisecond = segment.frame_rate / 1000
    maximum_miliseconds = MAXIMUM_SAMPLES * (segment.frame_rate / 1000)

    if maximum_miliseconds < abs(miliseconds):
        maximum_miliseconds = copysign(MAXIMUM_SAMPLES, maximum_miliseconds)
        logger.warning(f"Number of miliseconds too large {miliseconds} [Fixup: using {maximum_miliseconds}]")
        miliseconds = maximum_miliseconds

    return miliseconds * frames_per_milisecond


def index_to_miliseconds(index: int, segment: pydub.AudioSegment, logger: Logger) -> float:
    """
    Converts a sample index to miliseconds within the audio segment (untested)
    Args:
    :param index:   a sample index within the audio segment
    :param segment: a segment of an aduio recording
    :param logger:  a Logger class to use to record warning and/or debug information
    """
    frames_per_milisecond: float = segment.frame_rate / 1000

    if MAXIMUM_SAMPLES < abs(index):
        maximum_index: int = int(copysign(MAXIMUM_SAMPLES, index))
        logger.warning(f"Sample index magnitude too large {index} [Fixup: using {maximum_index}]")
        index = maximum_index

    return index / frames_per_milisecond


def to_miliseconds(value: Union[str, float, int], segment_miliseconds: int, logger: Logger) -> int:
    """
    Converts a string, float, or integer value to miliseconds

    - numeric values over 1 are treated as miliseconds (requiring no conversion) e.g., 1.1 or 123456
    - numeric values between 0.0 and 1.0 are treated as decimal percentage of the segement length, e.g., 0.5275
    - string values ending with '%' are treated as a percentage of the segement length, e.g., '99.99%'
    - string values ending with 's', 'sec', 'secs', or 'seconds' are treated as seconds, e.g., '27s', '250 sec', or '9.3 seconds'
    - string values ending with '', 'ms', or 'miliseconds' are treated as miliseconds, e.g., '33750', '5960444.8ms', '7600000000 miliseconds'

    Args:
    :param value:               duration as a percent of the audio segment, number of seconds, or number of miliseconds as a string, float, or integer value
    :param segment_miliseconds: the length of the aduio segment to use to calculate a miliseconds percentage values (optional)
    :param logger:              a Logger class to use to record warning and/or debug information
    """
    if isinstance(value, int) or isinstance(value, float):
        return int(segment_miliseconds * value if 0 <= value <= 1 else value)  # decimal percentage of the segment or already miliseconds

    note: str = "Durations are numeric values, or strings ending with one of the following units: 's', 'sec', 'secs', 'seconds', 'ms', 'miliseconds', or '%'"

    if not isinstance(value, str):
        logger.warning(f"Duration argument type not valid {value} of {type(value)} [Fixup: returning 0]")
        logger.warning(note)
        return 0

    string: str = value.replace(' ', '')

    if '' == string:
        return 0

    parts: [str] = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number: float = float(parts[1])
    units: str = parts[2]

    try:
        if '' == units and 0 <= number <= 1:  # floating point percentage e.g., 0.5275
            return int(segment_miliseconds * number)
        if '%' == units:  # string percentage e.g., '99.99%'
            return int(segment_miliseconds * number / 100)
    except TypeError:
        logger.error("When expressing a duration as a percentage an audio segment length (in miliseconds) is required")
        return 0

    if 's' == units or 'sec' == units or 'secs' == units or 'seconds' == units:
        return int(number * 1000)
    if '' == units or 'ms' == units or 'miliseconds' == units:
        return int(number)

    logger.warning(f"Duration argument units invalid, {string} [Fixup: treating as {number} miliseconds]")
    logger.warning(note)

    return int(number)


def parse_common_arguments(arguments: {}, recording: pydub.AudioSegment, logger: Logger) -> (pydub.AudioSegment, int, int, int):
    """
    Extracts common slicer processing arguments
    Args:
    :param arguments: slicer arguments from which common ones will be parsed, validated, and returned
    :param recording: the downloaded aduio recording to be sliced
    :param logger:    a Logger class to use to record warning and/or debug information
    """
    recording_ms: int = len(recording)

    begin: int = to_miliseconds(arguments['begin'], recording_ms, logger) if 'begin' in arguments else 0
    end: int = to_miliseconds(arguments['end'], recording_ms, logger) if 'end' in arguments else recording_ms
    clip_size: int = to_miliseconds(arguments['clip_size'], recording_ms, logger) if 'clip_size' in arguments else DEFAULT_CLIP_SIZE_MILISECONDS
    clips: int = arguments['clips'] if 'clips' in arguments else DEFAULT_CLIPS_PER_STAGE

    note = "Note: use values between 0.0 and 1.0 ('100%') to calculate a percentage of the clip duration as the starting or stopping point for clip generation"

    if 0 > begin:
        logger.warning(f"Argument 'begin' {begin} invalid, must be between 0 and the recording length in miliseconds {recording_ms} [Fixup: using 0 ms]")
        logger.warning(f"Omit or set the 'begin' argument to 0 to start at the first sample of the recording")
        begin = 0
        if note is not None:
            logger.warning(note)
            note = None
    if recording_ms < begin:
        logger.warning(f"Argument 'end' {begin} invalid, must be between 0 and the recording length in miliseconds {recording_ms} [Fixup: using {recording_ms} ms]")
        begin = recording_ms
        if note is not None:
            logger.warning(note)
            note = None
    if 0 > end:
        logger.warning(f"Argument 'end' {end} invalid, must be between 0 and the recording length in miliseconds {recording_ms} [Fixup: using 0 ms]")
        end = 0
        if note is not None:
            logger.warning(note)
            note = None
    if recording_ms < end:
        logger.warning(f"Argument 'end' {end} invalid must, be between 0 and the recording length in miliseconds {recording_ms} [Fixup: using {recording_ms} ms]")
        logger.warning(f"Omit or set the 'end' argument to 1 to stop at the last sample of the recording")
        end = recording_ms
        if note is not None:
            logger.warning(note)
            note = None
    if begin > end:
        begin, end = end, begin
        logger.warning(f"Argument begin {end} and end {begin} were reversed [Fixup: using {begin},{end}]")

    if note is not None:
        logger.debug(note)

    return recording[begin:end], miliseconds_to_index(begin, recording, logger), clip_size, clips
