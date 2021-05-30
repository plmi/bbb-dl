from abc import ABC, abstractmethod, ABCMeta

class MediaElement(ABC):
  __metaclass__ = ABCMeta

  def __convert_to_seek_time(self, ms):
    """convert milliseconds to a ffmpeg compatible seek time e.g. 00:02:24.083
    returns an empty string if no input was provided"""
    try:
      val = int(ms)
    except:
      return ""
    ss = int((ms // 1000) % 60)
    mm = int((ms // (60 * 1000)) % 60)
    hh = int((ms // (60 * 60 * 1000)) % 24)
    ms = int(ms - (hh * 3600000) - (mm * 1000 * 60) - (ss * 1000))
    return "{0:02d}:{1:02d}:{2:02d}.{3:03d}".format(hh, mm, ss, ms)

  @abstractmethod
  def __init__(self, type, name, source, start, end):
    self.type = type
    self.name = name
    self.source = source
    self.start = start
    self.end = end

  @property
  def start_timecode(self):
    return self.__convert_to_seek_time(self.start)

  @property
  def end_timecode(self):
    return self.__convert_to_seek_time(self.end)
