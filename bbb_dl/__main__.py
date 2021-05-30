 #!/usr/bin/env python3

 # Author: Michael P.
 # Info: downloads bbb meeting as offline video

import os
import sys
import glob
import uuid
import requests
import concurrent.futures
import bbb_dl.ffmpeg as ffmpeg
from .models.slide import Slide
from .models.deskshare import Deskshare
from .models.media_type import MediaType
from bbb_dl.bbb_downloader import BBBDownloader

def print_usage():
  print(f'url missing')
  print(f'usage: {sys.argv[0]} [url]')

def clear_files():
  """remove all temporary files"""
  files = ['./audio.opus', './deskshare.webm', \
    './webcams.webm', './concat.mp4', './playlist.txt']
  for f in files:
    try:
      os.remove(f)
    except:
      pass
  for pattern in ['./image*.png', './image*.mp4']:
    try:
      files = glob.glob(pattern, recursive=False)
      for image in files:
        os.remove(image)
    except Exception as e:
      print('exection' + str(e))

def save_playlist(media_elements, filename):
  """creates a ffmpeg compatible input playlist"""
  with open(filename, 'w') as f:
    for entry in media_elements:
      f.write(f'file {entry.name}.mp4\n')
  return filename
     
PLAYLIST = 'playlist.txt'
CONCAT_FILE = 'concat.mp4'
OUTPUT_FILE = 'output.mp4'
AUDIO_FILE = 'audio.opus'

def entry_point():

  if len(sys.argv) <= 1:
    print_usage()
    sys.exit(1)

  bbb_dl = BBBDownloader(sys.argv[1])

  slides = bbb_dl.download_slides()
  sequences = []

  if any('deskshare' in slide.source for slide in slides):
    deskshare = bbb_dl.download_deskshare()
    # create deskshares with timestamps of corresponding slides
    sequences = [Deskshare(uuid.uuid4().hex, deskshare, x.start, x.end)
      for x in slides if 'deskshare' in x.source]
    slides[:] = [x for x in slides if 'deskshare' not in x.source]

  media_elements = slides + sequences
  # bring deskshares into correct position
  media_elements.sort(key=lambda x: x.start)

  for x in media_elements:
    if x.type == MediaType.DESKSHARE:
      ffmpeg.extract_sequence(x.source, x.start_timecode, x.end_timecode, f'{x.name}.mp4')
    else:
      duration = (x.end - x.start) / 1000
      ffmpeg.convert_image_to_video(f'{x.name}.png', duration, f'{x.name}.mp4')

  playlist = save_playlist(media_elements, PLAYLIST)
  video = ffmpeg.concat_videos(playlist, CONCAT_FILE)
  audio = bbb_dl.download_webcams()
  audio = ffmpeg.demux_audio(audio, AUDIO_FILE)
  ffmpeg.mux_video_audio(video, audio, OUTPUT_FILE)
  clear_files()

if __name__ == "__main__":
  entry_point()
