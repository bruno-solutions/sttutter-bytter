import taglib


class Tagger:
    def __init__(self, metadata):
        self.tags = self.parse_metadata(metadata)

    @staticmethod
    def parse_metadata(metadata):
        """
        Convert a downloaded file's information dictionary into Sttutter audio file tags
        """

        tags = {}

        keys = ['id', 'title', 'description', 'uploader', 'upload_date', 'channel', 'channel_id', 'channel_url', 'playlist', 'playlist_index', 'age_limit', 'is_live', 'view_count', 'like_count', 'thumbnail', 'webpage_url']

        for key in keys:
            if key in metadata:
                if metadata[key] is not None:
                    tags[key.replace('_', ' ')] = metadata[key] if metadata[key] is str else str(metadata[key])

        keys = ['categories', 'tags']
        key2tag = {'categories': 'category', 'tags': 'tag'}

        for key in keys:
            if key in metadata:
                for index, value in enumerate(metadata[key]):
                    value = ' '.join([word.title() if word not in "a an and as but by for in if nor of off on onto or out so the to up with yet" else word for word in value.capitalize().split(' ')])
                    if key2tag[key] in tags:
                        tags[key2tag[key]] += ' | ' + value
                    else:
                        tags[key2tag[key]] = value

        return tags

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
            if -1 == '| ' + self.tags[tag] + ' |'.find('| ' + value + ' |'):
                value = self.tags[tag] + ' | ' + value
            else:
                value = self.tags[tag]

        self.set(tag, value)

    def delete(self, tag):
        """
        Delete a tag
        """
        self.tags[tag] = None

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

    def write_tags(self, filename):
        """
        Add Sttutter tags to an audio file
        """
        audio = taglib.File(filename)
        audio.tags = self.tags
        audio.save()
