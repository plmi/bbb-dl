#!/usr/bin/env python3

import subprocess

def demux_audio(media_file, output_file):
  """extract audio stream from video container"""
  subprocess.call(['ffmpeg', '-i', media_file, '-vn', '-acodec', 'copy', output_file])
  return output_file

def mux_video_audio(video_file, audio_file, output_file):
  """merge an audio and video stream into media container"""
  subprocess.call(['ffmpeg', '-i', video_file, '-i', audio_file, '-strict', '-2', '-c', 'copy', output_file])
  return output_file

def concat_videos(file_list, output_file):
  """merge multiple videos into one sequence"""
  subprocess.call(['ffmpeg', '-f', 'concat', '-i', f'{file_list}', '-c', 'copy', output_file])
  return output_file

def convert_image_to_video(input_image, duration, output_file):
  """creates video from image of specified duration"""
  subprocess.call(['ffmpeg', '-framerate', f'1/{duration}', '-i', input_image, \
    '-filter:v', 'pad=ih*16/9:ih:(ow-iw)/2:(oh-ih)/2,scale=1280:-1', '-c:v', \
    'libx264', '-preset', 'fast', '-r', '24', '-pix_fmt', 'yuv420p', output_file])
  return output_file

def extract_sequence(video_file, ss_from, ss_to, output_file):
  """extracts a video sequence from a given file and. returns the output file."""
  # reencoding is required to cut precisely because not all frames are keyframes!
  command = ['ffmpeg', '-i', video_file, '-ss', ss_from, '-c:v', 'libx264', \
    '-pix_fmt', 'yuv420p', output_file]
  if ss_to:
    command[5:5] = ['-to', ss_to]
  subprocess.call(command)
  return output_file
