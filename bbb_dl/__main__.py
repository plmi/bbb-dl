 #!/usr/bin/env python3

 # Author: Michael P.
 # Info: downloads bbb meeting as offline video

import os
import sys
import re
import math
import glob
import requests
import warnings
import urllib.request
import concurrent.futures
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import bbb_dl.ffmpeg as ffmpeg
from .models.slide import Slide

class BBBDownloader:
  """This implementation provides methods for downloading audio, deskshare and slides
  from a given bbb meeting url"""
  def __init__(self, url):
    self.url = url
    self.meeting_id = re.search(r'=([\da-z-]+)', url).group(1)
    self.host = re.search(r'https://.*?\/', url).group(0)

  @property
  def deskshare_url(self):
    return f'{self.host}presentation/{self.meeting_id}/deskshare/deskshare.webm'

  @property
  def webcams_url(self):
    return f'{self.host}presentation/{self.meeting_id}/video/webcams.webm'

  def __download(self, url, destination):
    """downloads file from url with progress hook and returns filepath"""
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', 'whatever')
    filename, headers = opener.retrieve(url, destination, reporthook=self.__progress_callback)
    return filename

  def __download_image(self, slide):
    """downloads slide to disk"""
    response = requests.get(self.host + slide.url)
    print('Process slide ..: ' + slide.name, end='\r')
    with open(f'{slide.name}.png', 'wb') as f:
      f.write(response.content)

  def __progress_callback(self, block, block_size, remote_size):
     percent = 100.0 * block *block_size /remote_size
     if percent > 100:
         percent = 100
     print('Downloading: %.2f%%' % percent, end='\r')

  def __get_images(self, url):
    """crawls meeting page for all images of the slideshow"""
    content = None
    # canvas not available with regular GET request
    # probably rendered afterwards with js
    with sync_playwright() as p:
      browser = p.firefox.launch(headless=True)
      page = browser.new_page()
      page.goto(url)
      page.wait_for_selector("#svgfile")
      content = page.query_selector_all("#svgfile >> image[visibility=hidden]")
      content = page.content()
      browser.close()
    return content

  def __create_slides(self, content):
    """creates array of slide objects from html source"""
    soup = BeautifulSoup(content, 'html.parser')
    slides = []
    for image in soup.find_all('image'):
      duration = math.ceil(float(image.get('out')) - float(image.get('in')))
      # TODO: one of the last images is as
      # long as the whole slideshow?
      if duration > 4000:
        break
      slide = Slide(image.get('id'), duration, image.get('xlink:href'))
      slides.append(slide)
    return slides

  def download_deskshare(self):
    """downloads deskshare.web and returns the filepath"""
    return self.__download(self.deskshare_url, 'deskshare.webm')

  def download_webcams(self):
    """downloads webcams.web and returns the filepath"""
    return self.__download(self.webcams_url, 'webcams.webm')

  def download_slides(self, url):
    """downloads all images of a slideshow and returns an array of all slides"""
    content = self.__get_images(url)
    slides = self.__create_slides(content)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
      executor.map(self.__download_image, slides)
    return slides

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
  warnings.filterwarnings("ignore", category=DeprecationWarning) 

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
