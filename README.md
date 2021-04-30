# bbb-dl

Tool to download BBB meetings as an offline video.  
Currently deskshare, audio and slideshows are supported.

## Requirements

* ffmpeg

Required python packages:
* [playwright](https://github.com/microsoft/playwright-python)
* requests
* BeautifulSoup4

Install python dependencies:
```bash
$ pip install -r requirements.txt
```

Additionally you need to install playwright browser binaries.  
See playwright's Github page for further information.
```bash
$ playwright install
```

## How to use

Invoke the program with your BBB meeting url:
```bash
$ python3 bbb-dl.py 'https://<host>/playback/presentation/2.0/playback.html?meetingId=<meeting_url>'
```

The final output is a mp4 video container with x264 video and opus audio stream.
