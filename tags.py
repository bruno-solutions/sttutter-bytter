import taglib


def parse_metadata(metadata):
    """
    Convert a downloaded file's information dictionary into Sttutter audio file tags
    """

    tags = {}

    keys = ['id', 'title', 'description', 'uploader', 'upload_date', 'channel', 'channel_id', 'channel_url', 'playlist', 'playlist_index', 'age_limit', 'is_live', 'view_count', 'like_count', 'thumbnail', 'webpage_url']

    for key in keys:
        if key in metadata:
            tags[key.replace('_', ' ')] = metadata[key]

    keys = ['categories', 'tags']
    key2tag = {'categories': 'category', 'tags': 'tag'}

    for key in keys:
        if key in metadata:
            for index, value in enumerate(metadata[key]):
                if key2tag[key] in tags:
                    tags[key2tag[key]] += ' | '
                tags[key2tag[key]] += value

    return tags


def write_tags(filename, tags):
    """
    Add Sttutter tags to an audio file
    """

    audio = taglib.File(filename)
    audio.tags = tags
    audio.save()
