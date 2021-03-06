#!/usr/bin/env python3

from .media_element import MediaElement
from .media_type import MediaType

class Slide(MediaElement):
  def __init__(self, name, source, start, end):
    super().__init__(MediaType.SLIDE, name, source, start, end)
