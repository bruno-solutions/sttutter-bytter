from __future__ import unicode_literals
import youtube_dl


def downloader(url):
    # Create the logging for youtubedl to accept in case of errors
    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')

    # Our properties for the output file
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    # Use youtubedl to download the wav file
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(['whatever url we want'])
