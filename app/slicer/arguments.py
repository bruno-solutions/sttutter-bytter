import re

from configuration import DEFAULT_CLIP_SIZE_MILISECONDS, DEFAULT_CLIPS


def to_decibels(value):
    if isinstance(value, str):
        pass
    return value


def to_sample_index(value):
    if isinstance(value, str):
        pass
    return value


def to_miliseconds(value, recording, logger):
    if isinstance(value, int) or isinstance(value, float):
        return len(recording) * value if 0 <= value <= 1 else value  # decimal percentage or miliseconds

    note = "Durations are numeric (int or float) values or strings ending with one of the following: 's', 'sec', 'secs', 'seconds', 'ms', 'miliseconds', or '%'"

    if not isinstance(value, str):
        logger.warning(f"Duration argument type not valid {value} of {type(value)} [Fixup: returning 0]")
        logger.warning(note)
        return 0

    string = value.replace(' ', '')
    if '' == string:
        string = '0'
    parts = re.split(r'([-+]?[.\d]+)(.*)', string if '' != string else '0')
    number = float(parts[1])
    units = parts[2]
    if '' == units and 0 <= number <= 1:  # decimal percentage
        number = len(recording) * number
    elif '%' == units:
        number = len(recording) * number / 100
    elif 's' == units or 'sec' == units or 'secs' == units or 'seconds' == units:
        number = number * 1000
    elif '' == units or 'ms' == units or 'miliseconds' == units:
        number = number
    else:
        logger.warning(f"Duration argument units invalid, {string} [Fixup: treating as {number} miliseconds]")
        logger.warning(note)
    return int(number)


def parse_common_arguments(arguments, recording, logger):
    recording_length_in_miliseconds = len(recording)

    begin = to_miliseconds(arguments['begin'], recording, logger) if 'begin' in arguments else 0.0
    end = to_miliseconds(arguments['end'], recording, logger) if 'end' in arguments else recording_length_in_miliseconds
    clip_size: int = to_miliseconds(arguments['clip_size'], recording, logger) if 'clip_size' in arguments else DEFAULT_CLIP_SIZE_MILISECONDS
    clips: int = arguments['clips'] if 'clips' in arguments else DEFAULT_CLIPS

    note = "Note: use values between 0.0 and 1.0 ('100%') to calculate a percentage of the clip duration as the starting or stopping point for clip generation"

    if 0 > begin:
        logger.warning(f"Argument 'begin' {begin} invalid, must be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using 0 ms]")
        logger.warning(f"Omit or set the 'begin' argument to 0 to start at the first sample of the recording")
        begin = 0
        if note is not None:
            logger.warning(note)
            note = None
    if recording_length_in_miliseconds < begin:
        logger.warning(f"Argument 'end' {begin} invalid, must be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using {recording_length_in_miliseconds} ms]")
        begin = recording_length_in_miliseconds
        if note is not None:
            logger.warning(note)
            note = None
    if 0 > end:
        logger.warning(f"Argument 'end' {end} invalid, must be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using 0 ms]")
        end = 0
        if note is not None:
            logger.warning(note)
            note = None
    if recording_length_in_miliseconds < end:
        logger.warning(f"Argument 'end' {end} invalid must, be between 0 and the recording length in miliseconds {recording_length_in_miliseconds} [Fixup: using {recording_length_in_miliseconds} ms]")
        logger.warning(f"Omit or set the 'end' argument to 1 to stop at the last sample of the recording")
        end = recording_length_in_miliseconds
        if note is not None:
            logger.warning(note)
            note = None
    if begin > end:
        begin, end = end, begin
        logger.warning(f"Argument begin {end} and end {begin} were reversed [Fixup: using {begin},{end}]")

    if note is not None:
        logger.debug(note)

    return recording[begin:end], int(recording.frame_rate * begin / 1000), clip_size, clips
