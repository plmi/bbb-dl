 #!/usr/bin/env python3

 # Author: Michael P.
 # Info: downloads bbb meeting as offline video

import os
import sys
import glob
import requests
import concurrent.futures
import bbb_dl.ffmpeg as ffmpeg
from .models.slide import Slide
from bbb_dl.bbb_downloader import BBBDownloader

def print_usage():
  print(f'url missing')
  print(f'usage: {sys.argv[0]} [url]')

def clear_files():
  """remove all temporary files"""
  files = ['./audio.opus', './deskshare.webm', \
    './webcams.webm', './concat.mkv', './playlist.txt']
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

def create_playlist(slides, filename):
  """creates input file for ffmpeg"""
  for slide in slides:
    with open(filename, 'a') as f:
      f.write(f'file {slide.name}.mp4\n')

def is_deskshare_available(url):
  """check if deskshare is available. return true if deskshare
  was found else false"""
  headers = { 'User-Agent': 'whatever' }
  response = requests.head(url, headers=headers)
  return response.status_code == 200

def entry_point():
  #warnings.filterwarnings("ignore", category=DeprecationWarning) 

  if len(sys.argv) <= 1:
    print_usage()
    sys.exit(1)

  bbb_dl = BBBDownloader(sys.argv[1])
  video = None
  if is_deskshare_available(bbb_dl.deskshare_url):
    print('deskshare found..')
    video = bbb_dl.download_deskshare()
  else:
    print('slides found..')
    slides = bbb_dl.download_slides(sys.argv[1])
    print('create slideshow...')
    for slide in slides:
      ffmpeg.convert_image_to_video(f'{slide.name}.png', slide.duration, f'{slide.name}.mp4')
    playlist = 'playlist.txt'
    create_playlist(slides, playlist)
    video = ffmpeg.concat_videos(playlist)

  webcams = bbb_dl.download_webcams()
  print('demux audio..')
  audio = ffmpeg.demux_audio(webcams)
  print('mux video+audio..')
  ffmpeg.mux_video_audio(video, audio)
  print('clear files..')
  clear_files()
  print('output.mp4 created')

if __name__ == "__main__":
  entry_point()
