"""
Taken from
https://github.com/ndonkoHenri/Flet-Custom-Controls/commit/e1958e998ef0b16449cb58a13a94251f38ab2dac
with MIT license:
https://github.com/ndonkoHenri/Flet-Custom-Controls/commit/8a8e920f0382734eef09734ea87a4c18d2cd21ed#diff-c693279643b8cd5d248172d9c22cb7cf4ed163a3c98c8a3f69c2717edd3eacb7
"""
from collections import namedtuple
from typing import Optional, Callable
import flet as ft
import flet.canvas as cv


class SizeAwareControl(cv.Canvas):
    def __init__(self, content: Optional[ft.Control] = None, resize_interval: int=100, on_resize: Optional[Callable]=None, **kwargs):
        """
        :param content: A child Control contained by the SizeAwareControl. Defaults to None.
        :param resize_interval: The resize interval. Defaults to 100.
        :param on_resize: The callback function for resizing. Defaults to None.
        :param kwargs: Additional keyword arguments(see Canvas properties).
        """
        super().__init__(**kwargs)
        self.content = content
        self.resize_interval = resize_interval
        self.on_resize = self.__handle_canvas_resize
        self.resize_callback = on_resize
        self.size = namedtuple("size", ["width", "height"], defaults=[0, 0])

    def __handle_canvas_resize(self, e):
        """
        Called every resize_interval when the canvas is resized.
        If a resize_callback was given, it is called.
        """
        self.size = (int(e.width), int(e.height))
        self.update()
        if self.resize_callback:
            self.resize_callback(e)