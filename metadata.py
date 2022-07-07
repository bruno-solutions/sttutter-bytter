import json

import taglib


def write_metadata(filename):
    audio = taglib.File(filename)
    # Use json file as dict and loop through to get the tags we want
    with open('./cache/ytdl-fullsong.info.json') as json_file:
        info_dict = json.load(json_file)
        tags_array = ['id', 'title', 'description', 'upload_date', 'uploader', 'channel_id', 'channel_url',
                      'webpage_url', 'thumbnail', 'categories', 'tags', 'age_limit', 'is_live', 'view_count',
                      'like_count', 'channel', 'playlist', 'playlist_index']
        for tag in tags_array:
            if tag == 'tags' or tag == 'categories':
                for index, metadata in enumerate(info_dict[tag]):
                    audio.tags[f'{tag}{index}'] = str(metadata)
            else:
                audio.tags[tag] = str(info_dict[tag])

    audio.save()
