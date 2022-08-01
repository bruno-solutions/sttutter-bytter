import json
import os
import re
from typing import List, Union

from configuration.constants import APPLICATION_NAME
from logger import Logger

# Notes:
#      - tags use a spaces to separate words
#      - keys use an underscore to separate words

multivalue_key_to_tag: {} = {
    'categories': 'category',  # [RIFF:LIST:id3 :ID3 :TXXX:CATEGORY]
    'tags': 'tag', 'genres': 'genre'  # [RIFF:LIST:id3 :ID3 :TXXX:TAG]
}
multivalue_keys: [] = list(k for k, _ in multivalue_key_to_tag.items())
tag_to_multivalue_key: {} = dict((v, k) for k, v in multivalue_key_to_tag.items())
multivalue_tags: [] = list(k for k, _ in tag_to_multivalue_key.items())

# Empirically discovered RIFF chuck labels using Audacity, TagScanner, and Hxd Hex Editor (Audacity and TagScanner disagree on some of these)

monovalue_keys: [] = [
    APPLICATION_NAME,  # [RIFF:LIST:id3 :ID3 :TXXX:SOUNDBYTE]
    'age_limit',  # [RIFF:LIST:id3 :ID3 :TXXX:AGE LIMIT]
    'album',  # Album Title [Audacity][Fixed Tag] [RIFF:LIST:INFO:IPRD] or [RIFF:LIST:id3 :ID3 :TALB]
    'album_artist',  # Band [Audacity]
    'application',  # [RIFF:LIST:id3 :ID3 :TXXX:APPLICATION]
    'artist',  # Artist Name [Audacity][Fixed Tag] [RIFF:LIST:INFO:IART] or [RIFF:LIST:id3 :ID3 :TPE1]
    'asr',  # [RIFF:LIST:id3 :ID3 :TXXX:ASR]
    'bit_rate',  # [RIFF:LIST:id3 :ID3 :TXXX:BIT RATE]
    'bpm',  # BPM (beats per minute) [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:BPM (beats per minute)]
    'channel',  # [RIFF:LIST:id3 :ID3 :TXXX:CHANNEL]
    'channel_id',  # [RIFF:LIST:id3 :ID3 :TXXX:CHANNEL ID]
    'channel_url',  # [RIFF:LIST:id3 :ID3 :TXXX:CHANNEL URL]
    'channels',  # [RIFF:LIST:id3 :ID3 :TXXX:CHANNELS]
    'clip_title',  # [RIFF:LIST:id3 :ID3 :TXXX:CLIP TITLE]
    'comment',  # [RIFF:LIST:INFO:ICMT]
    'comments',  # Comments [Audacity][Fixed Tag] [RIFF:LIST:id3 :ID3 :COMM]
    'composer',  # Composer [Audacity] [RIFF:LIST:id3 :ID3 :TCOM]
    'conductor',  # Conductor [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:Conductor]
    'contentgroup',  # Content group description [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:Content group description] or [RIFF:LIST:id3 :ID3 :TIT1]
    'converter',  # [RIFF:LIST:id3 :ID3 :TXXX:CONVERTER]
    'copyright',  # Copyright message [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:Copyright message]
    'cover',  # [RIFF:LIST:id3 :ID3 :TXXX:COVER]
    'date',  # [RIFF:LIST:id3 :ID3 :TDRC]
    'description',  # [RIFF:LIST:id3 :ID3 :TXXX:DESCRIPTION]
    'disc',  # [RIFF:LIST:id3 :ID3 :TXXX:DISC]
    'duration',  # [RIFF:LIST:id3 :ID3 :TXXX:DURATION]
    'encodedby',  # Encoded by [Audacity] [RIFF:LIST:id3 :ID3 :TXXX : Encoded by] or [RIFF:LIST:id3 :ID3 :TENC]
    'filename',
    'filesize',  # [RIFF:LIST:id3 :ID3 :TXXX:FILESIZE]
    'frame_rate',  # [RIFF:LIST:id3 :ID3 :TXXX:FRAME RATE]
    'full_scale_decibels',  # [RIFF:LIST:id3 :ID3 :TXXX:FULL SCALE DECIBELS]
    'genre',  # Genre [Audacity][Fixed Tag] [RIFF:LIST:INFO:IGNR] or [RIFF:LIST:id3 :ID3 :TCON]
    'grouping',  # [RIFF:LIST:id3 :ID3 :TXXX:Content group description]
    'key',  # Initial Key [Audacity] [RIFF:LIST:id3 :ID3 :TKEY]
    'lyricist',  # Lyricist [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:Lyricist]
    'id',  # [RIFF:LIST:id3 :ID3 :TXXX:ID]
    'is_live',  # [RIFF:LIST:id3 :ID3 :TXXX:IS LIVE]
    'isrc',  # ISRC (international standard recording code) [Audacity] [RIFF:LIST:id3 :ID3 :TSRC]
    'length',  # Length [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:Length]
    'like_count',  # [RIFF:LIST:id3 :ID3 :TXXX:LIKE COUNT]
    'max',  # [RIFF:LIST:id3 :ID3 :TXXX:MAX]
    'max_full_scale_decibels',  # [RIFF:LIST:id3 :ID3 :TXXX:MAX FULL SCALE DECIBELS]
    'max_possible_amplitude',  # [RIFF:LIST:id3 :ID3 :TXXX:MAX POSSIBLE AMPLITUDE]
    'origartist',  # Original artist(s) [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:ORIGARTIST] or [RIFF:LIST:id3 :ID3 :TOPE]
    'performer',  # [RIFF:LIST:id3 :ID3 :TXXX:PERFORMER]
    'playlist',  # [RIFF:LIST:id3 :ID3 :TXXX:PLAYLIST]
    'playlist_index',  # [RIFF:LIST:id3 :ID3 :TXXX:PLAYLIST INDEX]
    'publisher',  # [RIFF:LIST:id3 :ID3 :TXXX:PUBLISHER] or [RIFF:LIST:id3 :ID3 :TPUB]
    'remixedby',  # Interpreted, remixed, or otherwise modified by [Audacity] [RIFF:LIST:id3 :ID3 :TXXX:REMIXEDBY] or [RIFF:LIST:id3 :ID3 :TPE4]
    'rms',  # [RIFF:LIST:id3 :ID3 :TXXX:RMS]
    'sample_rate',  # [RIFF:LIST:id3 :ID3 :TXXX:SAMPLE RATE]
    'sample_width',  # [RIFF:LIST:id3 :ID3 :TXXX:SAMPLE WIDTH]
    'subtitle',  # Subtitle [Audacity]  # [RIFF:LIST:id3 :ID3 :TXXX:Subtitle]
    'thumbnail',  # [RIFF:LIST:id3 :ID3 :TXXX:THUMBNAIL]
    'title',  # Track Title [Audacity][Fixed Tag] [RIFF:LIST:INFO:INAM] or [RIFF:LIST:id3 :ID3 :TIT2:title]
    'totaldiscs',  # [RIFF:LIST:id3 :ID3 :TXXX:TOTALDISCS]
    'totaltracks',  # [RIFF:LIST:id3 :ID3 :TXXX:TOTALTRACKS]
    'track',  # [RIFF:LIST:id3 :ID3 :TXXX:TRACK]
    'tracknumber'  # Track Number [Audacity][Fixed Tag] [RIFF:LIST:INFO:ITRK] or [RIFF:LIST:id3 :ID3 :TRCK] track/total tracks
    'upload_date',  # [RIFF:LIST:id3 :ID3 :TXXX:UPLOAD DATE]
    'uploader',  # [RIFF:LIST:id3 :ID3 :TXXX:UPLOADER]
    'view_count',  # [RIFF:LIST:id3 :ID3 :TXXX:VIEW COUNT]
    'webpage_url',  # [RIFF:LIST:id3 :ID3 :TXXX:WEN PAGE URL]
    'www',  # [RIFF:LIST:id3 :ID3 :WWW] or [RIFF:LIST:id3 :ID3 :WXXX]
    'year'  # Year [Audacity][Fixed Tag] [RIFF:LIST:INFO:ICRD] or [RIFF:LIST:id3 :ID3 :TDRC] or [RIFF:LIST:id3 :ID3 :TYER]
    # Part of a set [Audacity] [RIFF:LIST:id3 :ID3 :TPOS] disc/total discs
]


def tag_to_key(tag: str):
    return tag.replace(' ', '_')


def key_to_tag(tag: str):
    return tag.replace('_', ' ')


def multivalue_tag_value_formatter(value: str):
    return ' '.join(re.sub(r"(\|)\1+", r"\1", re.sub(r'(\|\s*)', '|', re.sub(r'(\s*\|)', '|', value.replace(',', '|').replace(';', '|').replace(':', '|')))).strip('|').replace('|', ' | ').split())


def is_monovalue_key(key: str):
    return key in monovalue_keys


def is_multivalue_key(key: str):
    return key in multivalue_keys


def is_multivalue_tag(tag: str):
    return tag in multivalue_tags


class Tagger(object):
    def __init__(self):
        self.tags: dict[str, str] = {}

    def clear(self):
        self.tags = {}

    def list(self):
        """
        Retrieve the list of tag keys
        """
        return list(self.tags.keys())

    def add(self, tag: str, value):
        """
        Add a new tag (does not change tag value when the tag already exists)
        """
        if tag in self.tags:
            Logger.warning(f'Tag {tag} already exists with a value of {self.tags[tag]}. If it is OK to overwrite this tag use set() instead')
            return

        self.set(tag, value)

    def set(self, tag: str, value):
        """
        Set a tag value (silently overwritting where there is an existing value)
        """
        self.tags[tag] = str(value)

    def replace(self, tag: str, value):
        """
        Set and return the old value of a tag
        """
        old = self.get(tag)
        self.set(tag, value)
        return old

    def append(self, tag: str, value):
        """
        Append a value to a multi-value tag
        """
        if tag in self.tags:
            if -1 != ('| ' + self.tags[tag] + ' |').find('| ' + str(value) + ' |'):
                return
            value = self.tags[tag] + ' | ' + str(value)

        self.set(tag, value)

    def delete(self, tag: str):
        """
        Delete a tag (sliently allows tags that do not exist to be "deleted")
        """
        if tag in self.tags:
            del self.tags[tag]

    def remove(self, tag: str):
        """
        Delete and return the old value of a tag
        """
        old = self.get(tag)
        self.delete(tag)
        return old

    def get(self, tag: str):
        """
        Return the value of a tag
        """
        return self.tags[tag] if tag in self.tags else ''

    def exists(self, tag: str):
        """
        Return whether or not a tag exists
        """
        return tag in self.tags

    def derive_clip_title(self):
        if self.get('clip title'):
            return
        for tag in ['filename', 'title', 'subtitle', 'artist', 'album artist', 'album', 'performer', 'composer', 'conductor', 'webpage url', 'www']:
            value: str = self.get(tag)
            if value:
                self.set('clip title', f"{value}")
                return
        self.set('clip title', 'clip')

    # https://github.com/supermihi/pytaglib/blob/39aabb26f4d6016c110794361b20b7fb76e64ecc/src/taglib.pyx#L43

    def load_audio_file_tags(self, filename: str):
        """
        Read tags from an audio file
        """
        import pydub
        import taglib

        Logger.debug(f"Loading tags from audio file {filename}", separator=True)

        try:
            file: taglib.File = taglib.File(filename)
            metadata: {} = file.tags
            file.close()
        except IOError:
            Logger.warning(f"Audio file {filename} could not be opened to retrieve metadata")
            return self

        recording: pydub.AudioSegment = pydub.AudioSegment.from_file(filename)

        Logger.debug(f"Generating additional metadata values (minicking YouTube Download option 'writeinfojson': True)", separator=True)
        metadata['asr'] = recording.frame_rate
        metadata['channels'] = recording.channels
        metadata['converter'] = recording.converter
        metadata['duration'] = int(recording.duration_seconds)
        metadata['filesize'] = os.path.getsize(filename)
        metadata['frame rate'] = recording.frame_rate
        metadata['full scale decibels'] = recording.dBFS
        metadata['max full scale decibels'] = recording.max_dBFS
        metadata['max possible amplitude'] = recording.max_possible_amplitude
        metadata['max'] = recording.max
        metadata['rms'] = recording.rms
        metadata['sample width'] = recording.sample_width

        for tag, value in metadata.items():
            tag = tag.lower()
            value = value[0] if type(value) in (tuple, list) else str(value) if type(value) in (int, float) else value
            if is_multivalue_tag(tag):
                value = multivalue_tag_value_formatter(value)
                self.append(tag, value)
            else:
                self.set(tag, str(value))
            Logger.debug(f"[{tag}]:'{value}'")

        return self

    def write_audio_file_tags(self, filename: str):
        """
        Write tags to an audio file
        """
        import taglib

        Logger.debug(f"Saving tags to audio file {filename}", separator=True)

        for tag, value in self.tags.items():
            Logger.debug(f"[{tag}]:'{value}'")

        # https://github.com/supermihi/pytaglib/blob/main/src/taglib.pyx
        # https://github.com/supermihi/pytaglib/blob/39aabb26f4d6016c110794361b20b7fb76e64ecc/src/taglib.pyx#L173

        try:
            file: taglib.File = taglib.File(filename)
            file.tags = self.tags
            file.save()
            file.close()
        except IOError as error:
            Logger.error(f"Was not able to write audio file {filename} metadata {error}")

        return self

    def load_metadata_file(self, filename: str):
        """
        Read audio recording metadata from a YouTube Downloader format JSON file
        Args:
        :param filename: YouTube Downloader format JSON file containing audio file metadata
        """
        Logger.debug(f"Loading tags from metadata file {filename}", separator=True)

        try:
            with open(filename) as json_file:
                metadata = json.load(json_file)
        except IOError:
            Logger.warning(f"Metadata file {filename} not found")
            return self

        # We only handle metadata keys that are defined in this module (all others are ignored)

        for key in monovalue_keys:
            if key in metadata:
                if metadata[key] is not None:
                    self.set(key_to_tag(key), metadata[key] if metadata[key] is str else str(metadata[key]))

        for key in multivalue_key_to_tag:
            if key in metadata:
                for index, value in enumerate(metadata[key]):
                    value = ' '.join([word.title() if word not in "a an and as but by for in if nor of off on onto or out so the to up with yet" else word for word in value.capitalize().split(' ')])
                    if self.exists(multivalue_key_to_tag[key]):
                        self.set(multivalue_key_to_tag[key], f"{self.get(multivalue_key_to_tag[key])} | {value}")
                    else:
                        self.set(multivalue_key_to_tag[key], value)

        return filename

    def write_downloader_metadata(self, filename: str):
        """
        Write audio recording metadata to a YouTube Downloader format JSON file
        Args:
        :param filename: YouTube Downloader format JSON file to be created
        """
        Logger.debug(f"Saving tags to metadata file {filename}", separator=True)

        metadata: dict[str, Union[str, List[str]]] = {}

        for tag in self.tags:
            key = tag_to_key(tag)
            if is_monovalue_key(key):
                metadata[key] = self.get(tag)
                continue
            if is_multivalue_tag(tag):
                key = tag_to_multivalue_key[tag]
                metadata[key] = self.get(tag).split(' | ')

        try:
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(metadata, json_file, ensure_ascii=False, indent=4)
        except IOError as error:
            Logger.error(f"Was not able to overwrite YouTube Download metadata file {error}")

        return filename

    def synchronize_metadata(self, media_filename: str, metadata_filename: str):
        Logger.debug(f"Reading and rewriting metadata for:", separator=True)
        Logger.debug(f"  - Media (video or audio) file: {media_filename}")
        Logger.debug(f"  - YouTube Download metadata file: {metadata_filename}")

        self.clear()
        self.load_metadata_file(metadata_filename)
        self.load_audio_file_tags(media_filename)
        self.derive_clip_title()
        self.write_downloader_metadata(metadata_filename)
        self.write_audio_file_tags(media_filename)
