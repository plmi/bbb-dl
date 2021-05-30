#!/usr/bin/env python3

import subprocess

def demux_audio(media_file):
  """extract audio stream from video container"""
  filename = 'audio.opus'
  subprocess.call(['ffmpeg', '-i', media_file, '-vn', '-acodec', 'copy', filename], stderr=subprocess.DEVNULL)
  return filename

def mux_video_audio(video_file, audio_file):
  """merge an audio and video stream into media container"""
  filename = 'output.mp4'
  subprocess.call(['ffmpeg', '-i', video_file, '-i', audio_file, '-strict', '-2', '-c', 'copy', filename])
  return filename

def concat_videos(file_list):
  """merge multiple videos into one sequence"""
  filename = 'concat.mkv'
  subprocess.call(['ffmpeg', '-f', 'concat', '-i', f'{file_list}', '-c', 'copy', filename], stderr=subprocess.DEVNULL)
  return filename

def convert_image_to_video(input_image, duration, output_file):
  """creates video from image of specified duration"""
  subprocess.call(['ffmpeg', '-framerate', f'1/{duration}', '-i', input_image, '-c:v', \
    'libx264', '-preset', 'fast', '-r', '10', '-pix_fmt', 'yuv420p', output_file])
  return output_file
