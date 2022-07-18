import json
import re
from typing import List, Union

import taglib

from logger import Logger

multivalue_key_to_tag = {'categories': 'category', 'tags': 'tag', 'genres': 'genre'}
multivalue_keys = list(k for k, _ in multivalue_key_to_tag.items())
tag_to_multivalue_key = dict((v, k) for k, v in multivalue_key_to_tag.items())
multivalue_tags = list(k for k, _ in tag_to_multivalue_key.items())
monovalue_keys = ['id', 'artist', 'title', 'clip_title', 'date', 'filesize', 'duration', 'asr', 'frame_rate', 'sample_width', 'channels', 'rms', 'max', 'max_possible_amplitude', 'full_scale_decibels', 'max_full_scale_decibels', 'converter', 'description', 'uploader', 'upload_date', 'channel', 'channel_id', 'channel_url', 'playlist', 'playlist_index', 'age_limit', 'is_live', 'view_count', 'like_count', 'thumbnail', 'webpage_url']


def tag_to_key(tag: str):
    return tag.replace(' ', '_')


def key_to_tag(tag: str):
    return tag.replace('_', ' ')


def multivalue_tag_value_formatter(value):
    return ' '.join(re.sub(r"(\|)\1+", r"\1", re.sub(r'(\|\s*)', '|', re.sub(r'(\s*\|)', '|', value.replace(',', '|').replace(';', '|').replace(':', '|')))).strip('|').replace('|', ' | ').split())


def is_monovalue_key(key: str):
    return key in monovalue_keys


def is_multivalue_key(key: str):
    return key in multivalue_keys


def is_multivalue_tag(tag: str):
    return tag in multivalue_tags


class Tagger:
    def __init__(self, logger=Logger()):
        self.logger = logger
        self.tags: dict[str, str] = {}

    def list(self):
        """
        Retrieve the list of tag keys
        """
        return list(self.tags.keys())

    def add(self, tag, value):
        """
        Add a new tag (does not change tag value when the tag already exists)
        """
        if tag in self.tags:
            self.logger.warning(f'Tag {tag} already exists with a value of {self.tags[tag]}. If it is OK to overwrite this tag use set() instead')
            return

        self.set(tag, value)

    def set(self, tag, value):
        """
        Set a tag value (silently overwritting where there is an ex old value)
        """
        self.delete(tag)
        self.tags[tag] = str(value)

    def replace(self, tag, value):
        """
        Set and return the old value of a tag
        """
        old = self.get(tag)
        self.set(tag, value)
        return old

    def append(self, tag, value):
        """
        Append a value to a multi-value tag
        """
        if self.tags[tag] is not None:
            if -1 != ('| ' + self.tags[tag] + ' |').find('| ' + value + ' |'):
                return
            value = self.tags[tag] + ' | ' + value

        self.set(tag, value)

    def delete(self, tag):
        """
        Delete a tag (sliently allows tags that do not exist to be "deleted")
        """
        if tag in self.tags:
            del self.tags[tag]

    def remove(self, tag):
        """
        Delete and return the old value of a tag
        """
        old = self.get(tag)
        self.delete(tag)
        return old

    def get(self, tag):
        """
        Return the value of a tag
        """
        return self.tags[tag]

    # https://github.com/supermihi/pytaglib/blob/39aabb26f4d6016c110794361b20b7fb76e64ecc/src/taglib.pyx#L43

    def read_youtube_downloader_metadata(self, filename):
        """
        Read audio recording metadata from a YouTube Downloader format JSON file
        Args:
            :param filename: YouTube Downloader format JSON file containing audio file metadata
        """
        self.logger.debug(f"Loading tags from metadata file {filename}", separator=True)

        with open(filename) as json_file:
            metadata = json.load(json_file)

        tags: dict[str, str] = {}

        for key in monovalue_keys:
            if key in metadata:
                if metadata[key] is not None:
                    tags[key_to_tag(key)] = metadata[key] if metadata[key] is str else str(metadata[key])

        for key in multivalue_key_to_tag:
            if key in metadata:
                for index, value in enumerate(metadata[key]):
                    value = ' '.join([word.title() if word not in "a an and as but by for in if nor of off on onto or out so the to up with yet" else word for word in value.capitalize().split(' ')])
                    if multivalue_key_to_tag[key] in tags:
                        tags[multivalue_key_to_tag[key]] += ' | ' + value
                    else:
                        tags[multivalue_key_to_tag[key]] = value

        self.tags = tags

        return self

    def write_youtube_downloader_metadata(self, filename):
        """
        Write audio recording metadata to a YouTube Downloader format JSON file
        Args:
            :param filename: YouTube Downloader format JSON file to be created
        """
        self.logger.debug(f"Saving tags to metadata file {filename}", separator=True)

        metadata: dict[str, Union[str, List[str]]] = {}

        tags: dict[str, str] = self.tags

        for tag in tags:
            key = tag_to_key(tag)
            if is_monovalue_key(key):
                metadata[key] = tags[tag]
                continue
            if is_multivalue_tag(tag):
                key = tag_to_multivalue_key[tag]
                metadata[key] = tags[tag].split(' | ')

        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(metadata, json_file, ensure_ascii=False, indent=4)

        return self

    def read_audio_file_tags(self, filename):
        """
        Read tags from an audio file
        """
        self.logger.debug(f"Loading tags from audio file {filename}", separator=True)

        file = taglib.File(filename)
        tags = file.tags
        file.close()

        self.tags = {}

        for tag, value in tags.items():
            tag = tag.lower()
            value = value[0]
            if is_multivalue_tag(tag):
                self.tags[tag] = multivalue_tag_value_formatter(value)
            else:
                self.tags[tag] = str(value)
            self.logger.debug(f"[{tag}]:'{value}'")

        return self

    def write_audio_file_tags(self, filename):
        """
        Write tags to an audio file
        """
        self.logger.debug(f"Saving tags to audio file {filename}", separator=True)

        for tag, value in self.tags.items():
            self.logger.debug(f"[{tag}]:'{value}'")

        file = taglib.File(filename)
        file.tags = self.tags
        file.save()
        file.close()

        return self
