import json
from typing import List, Union

import taglib

from logger import Logger

single_value_keys = ['id', 'title', 'description', 'uploader', 'upload_date', 'channel', 'channel_id', 'channel_url', 'playlist', 'playlist_index', 'age_limit', 'is_live', 'view_count', 'like_count', 'thumbnail', 'webpage_url']
multiple_value_keys = ['categories', 'tags']
multiple_value_keys_to_tags = {'categories': 'category', 'tags': 'tag'}
tags_to_multiple_value_keys = dict((v, k) for k, v in multiple_value_keys_to_tags.items())


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
        Add a new tag (fails when the tag already exists)
        """
        if self.tags[tag] is not None:
            raise ReferenceError(f'Tag {tag} already exists with a value of {self.tags[tag]}. If it is OK to overwrite this tag use set() instead')
        self.set(tag, value)

    def set(self, tag, value):
        """
        Set a tag value (silently overwritting the old value)
        """
        self.delete(tag)
        self.tags[tag] = value

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
        Delete a tag
        """
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
        with open(filename) as json_file:
            metadata = json.load(json_file)

        tags: dict[str, str] = {}

        for key in single_value_keys:
            if key in metadata:
                if metadata[key] is not None:
                    tags[key.replace('_', ' ')] = metadata[key] if metadata[key] is str else str(metadata[key])

        for key in multiple_value_keys:
            if key in metadata:
                for index, value in enumerate(metadata[key]):
                    value = ' '.join([word.title() if word not in "a an and as but by for in if nor of off on onto or out so the to up with yet" else word for word in value.capitalize().split(' ')])
                    if multiple_value_keys_to_tags[key] in tags:
                        tags[multiple_value_keys_to_tags[key]] += ' | ' + value
                    else:
                        tags[multiple_value_keys_to_tags[key]] = value

        self.tags = tags

        return self

    def write_youtube_downloader_metadata(self, filename):
        """
        Write audio recording metadata to a YouTube Downloader format JSON file
        Args:
            :param filename: YouTube Downloader format JSON file to be created
        """
        metadata: dict[str, Union[str, List[str]]] = {}

        tags: dict[str, str] = self.tags

        for tag in tags:
            key = tag.replace(' ', '_').lower()
            if key in single_value_keys:
                metadata[key] = tags[tag]
                continue
            key = tags_to_multiple_value_keys[tag]
            if key in multiple_value_keys:
                metadata[key] = tags[tag].split(' | ')

        with open(filename) as json_file:
            json.dump(metadata, json_file)

        return self

    def read_audio_file_tags(self, filename):
        """
        Read tags from an audio file
        """
        self.logger.separator(mode='debug')
        self.logger.debug(f"Loading tags from audio file {filename}")

        file = taglib.File(filename)
        self.tags = file.tags
        file.close()

        for tag, value in self.tags:
            self.logger.debug(f"[{tag}]:'{value}'")

        return self

    def write_audio_file_tags(self, filename):
        """
        Write tags to an audio file
        """
        self.logger.separator(mode='debug')
        self.logger.debug(f"Saving tags to audio file {filename}")

        for tag, value in self.tags:
            self.logger.debug(f"[{tag}]:'{value}'")

        file = taglib.File(filename)
        file.tags = self.tags
        file.save()
        file.close()

        return self
