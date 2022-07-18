# sttutter-audio-clipifier
A tool to split audio tracks from online and local file system media sources

### Requirements

---

[`pydub`](https://github.com/jiaaro/pydub) uses [`ffmpeg`](https://ffmpeg.org/download.html) which is an executable program installed on your operating system. `ffmpeg` is invoked by `youtube-dl` using the Python `subprocess.Popen()` method and `subprocess.PIPE` pipes to receive the output of `ffmpeg` e.g.:

`subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)`

So `youtube-dl` can invoke `ffmpeg` the directory in which `ffmpeg` executable is installed must included in the system `Path`.

   - _Note: You cannot use the ffmpeg executable that you may have installed for Audacity._
---
[`spleeter`](https://github.com/deezer/spleeter) uses [`libsndfile`](http://www.mega-nerd.com/libsndfile/#Download) which must be installed and available on the system `Path`.

---

To obtain required third-party Python packages/modules for the application use PIP:

   - `pip install -r requirements.txt`

### I*nteractive* D*evelopment* E*nvironment* *configuration tips*

Information related to setting up your development environment to work with the code of this project

#### IntelliJ (e.g., Pycharm or IDEA)

  - Install the Python plugin `Ctrl+Alt+S`:

    https://www.jetbrains.com/help/idea/managing-plugins.html


  - Setup a Python virtual environment `Ctrl+Alt+Shift+S`:

    https://www.jetbrains.com/help/idea/creating-virtual-environment.html

#### VS Code
Move "launch.json" into ".vscode"
Edit the files where needed (insert local PATHS)

Test Launch Profile

Use pip install -r requirements.txt to install all needed dependencies
Use pip freeze requirements.txt to update the requirements.txt to update automatically

#### Visual Studio

#### Eclipse

