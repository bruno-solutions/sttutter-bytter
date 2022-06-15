"""A minimum download module for getting songs from outside sources."""

from download import getsong_with_ytdl, getsong_with_aria2c

#Default the use of aria2c
getsong = getsong_fast = getsong_with_aria2c

#Legacy
getsong_from_url = getsong_with_ytdl
