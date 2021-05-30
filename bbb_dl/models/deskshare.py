#!/usr/bin/env python3

from .media_element import MediaElement
from .media_type import MediaType

class Deskshare(MediaElement):
  def __init__(self, name, source, start, end):
    super().__init__(MediaType.DESKSHARE, name, source, start, end)
