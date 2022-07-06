:: Usage
:: ytd urls.txt

:: urls.txt (example)
:: https://youtu.be/Rl6fyhZ0G5E
:: https://youtu.be/u1xrNaTO1bI
:: https://youtu.be/pWxJEIz7sSA
:: https://youtu.be/qeMFqkcPYcg
:: https://youtu.be/I_izvAbhExY
:: https://youtu.be/FTQbiNvZqaY
:: https://youtu.be/XfR9iY5y94s

for /f "delims=" %%A in (%1) do start youtube-dl "%%A" -x --audio-format wav -o %%(channel)s.%%(title)s.%%(ext)s --add-metadata --xattrs

:: Notes:
:: https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl
:: https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template

:: test/example command line invocations
:: youtube-dl https://youtu.be/u1xrNaTO1bI -x -o %%(channel)s.%%(title)s.%%(ext)s --audio-format wav --add-metadata --xattrs --prefer-ffmpeg --postprocessor-args "-metadata comment='downloaded by youtube-dl'" --verbose
:: youtube-dl https://youtu.be/Rl6fyhZ0G5E -x -o %%(channel)s.%%(title)s.%%(ext)s --audio-format wav --add-metadata --xattrs --prefer-ffmpeg --verbose
:: youtube-dl https://youtu.be/pWxJEIz7sSA -x -o %%(channel)s.%%(title)s.%%(ext)s --audio-format wav --add-metadata --xattrs
