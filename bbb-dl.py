 #!/usr/bin/env python3

 # Author: Michael P.
 # Date: 04/29/2021

import os
import sys
import re
import warnings
import subprocess
import urllib.request

class BBBDownloader:

  def __init__(self, url):
    self.url = url
    regexp = r'=([\da-z-]+)'
    self.meeting_id = re.search(regexp, url).group(1)

  @property
  def deskshare_url(self):
    return f'https://bbb.itsec.techfak.fau.de/presentation/{self.meeting_id}/deskshare/deskshare.webm'

  @property
  def webcams_url(self):
    return f'https://bbb.itsec.techfak.fau.de/presentation/{self.meeting_id}/video/webcams.webm'

  def download(self, url, destination):
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', 'whatever')
    filename, headers = opener.retrieve(url, destination, reporthook=self.progress_callback)
    return filename

  def progress_callback(self, block, block_size, remote_size):
     percent = 100.0 * block *block_size /remote_size
     if percent > 100:
         percent = 100
     print('Downloading: %.2f%%' % percent, end='\r')

class Muxxer:

  def demux_audio(self, media_file):
    filename = 'audio.opus'
    subprocess.call(['ffmpeg', '-i', media_file, '-vn', '-acodec', 'copy', filename], stderr=subprocess.DEVNULL)
    return filename

  def mux_video_audio(self, video_file, audio_file):
    subprocess.call(['ffmpeg', '-i', video_file, '-i', audio_file, '-c', 'copy', 'output.mkv'], stderr=subprocess.DEVNULL)


def print_usage():
  print(f'url missing')
  print(f'usage: {sys.argv[0]} [url]')

def clear_files():
  os.remove('./audio.opus')
  os.remove('./deskshare.webm')
  os.remove('./webcams.webm')

def main():
  warnings.filterwarnings("ignore", category=DeprecationWarning) 

  if len(sys.argv) <= 1:
    print_usage()
    sys.exit(1)

  grabber = BBBDownloader(sys.argv[1])
  deskshare = grabber.download(grabber.deskshare_url, 'deskshare.webm')
  webcams = grabber.download(grabber.webcams_url, 'webcams.webm')

  muxxer = Muxxer()
  print('demux audio..')
  audio = muxxer.demux_audio(webcams)
  print('mux video+audio..')
  muxxer.mux_video_audio(deskshare, audio)

  clear_files()
  print('output.mkv created')

if __name__ == "__main__":
  main()
