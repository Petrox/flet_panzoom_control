"""Implements a pan and zoom control for flet UI framework."""
import flet as ft

from size_aware_control import SizeAwareControl


class PanZoom(ft.UserControl):
    """Pan and zoom control for flet UI framework.

    This control can be used to display a large image or other content that can be larger than the viewport.

    Important: the width and the height of the content must be specified in the constructor, since it is a write only
    property. Use PIL (pillow) to figure out the width and height of an image.

    By default, the content is centered in the viewport, and scaled to fit in the viewport with padding added to the
    sides or top and bottom if necessary.

    No warranty, no support, use at your own risk, etc.
    """
    content_with_padding: ft.Container or None

    def __init__(self, content: ft.Control, content_width: int, content_height: int, width: int = None,
                 height: int = None, padding_color=ft.colors.TRANSPARENT, on_pan_update=None, on_scroll=None, on_click=None,
                 max_scale=300.0, min_scale=0.1, start_scale=None, expand=False):
        super().__init__()
        self.expand = expand
        content.scroll = None
        content.expand = False
        if isinstance(content, ft.Image):
            content.fit = ft.ImageFit.COVER  # we want to cover the whole area even if we are stretching the image
        self.inner_content = content
        self.scroll_to_scale_factor = 0.001
        self.padding_color = padding_color
        self.content_with_padding = None
        self.width = width if width is not None else 30000  # will be reduced to window or dialog size
        self.height = height if height is not None else 30000
        self.innerstack = None
        self.start_scale = start_scale
        self.max_scale = max_scale
        self.min_scale = min_scale
        self.on_scroll_callback = on_scroll
        self.on_click_callback = on_click
        self.on_pan_update_callback = on_pan_update
        self.content_height = content_height
        self.content_width = content_width
        self.scale = 1.0 if start_scale is None else start_scale
        self.previous_scale = self.scale
        self.offset_x = 0
        self.offset_y = 0
        self.zoom_x = None  # the x coordinate of the point within the content where the mouse was when the zoom was triggered
        self.zoom_y = None  # the proper implementation should scale up and down around this point not the center or corner of the content
        self.border_x = None
        self.border_y = None
        self.viewport_height = None
        self.viewport_width = None

    def build(self):

        self.content_with_padding = ft.Container(height=self.content_height,
                                                 width=self.content_width,
                                                 bgcolor=self.padding_color,
                                                 expand=self.expand,
                                                 content=ft.Column(alignment=ft.MainAxisAlignment.CENTER,
                                                                   expand=self.expand,
                                                                   controls=[
                                                                       ft.Row(controls=[self.inner_content],
                                                                              expand=self.expand,
                                                                              alignment=ft.MainAxisAlignment.CENTER)])
                                                 )
        self.innerstack = ft.Stack(controls=[self.content_with_padding,
                                             ft.GestureDetector(on_pan_update=self.on_pan_update,
                                                                on_scroll=self.on_scroll_update,
                                                                on_tap_up=self.click_content)],
                                   left=0,
                                   top=0,
                                   width=self.width,
                                   height=self.height,
                                   expand=self.expand)
        self.main_control = SizeAwareControl(content=ft.Stack(controls=[self.innerstack]),
                                             expand=self.expand,
                                             on_resize=self.content_resize,
                                             width=self.width,
                                             height=self.height)
        return self.main_control

    def reset_content_dimensions(self):
        self.scale = None
        self.update_content_pos_and_scale()

    def update_content_pos_and_scale(self):
        if self.viewport_width is None or self.viewport_height is None or self.viewport_height == 0 or self.viewport_width == 0:
            return
        viewport_ratio = self.viewport_width / self.viewport_height
        content_ratio = self.content_width / self.content_height
        print(
            f"update_content_pos_and_scale1: {self.viewport_width} {self.viewport_height} {viewport_ratio} {self.content_width} {self.content_height} {content_ratio}")
        # we want to pad the image with a border on the sides or on top and below so that the resulting object has the same ratio as the viewport
        # this is necessary to avoid inactive zones on the sides or top and bottom (pan should work everywhere, not just on the image itself if it is very wide or very tall)
        if viewport_ratio > content_ratio:
            # viewport is wider than image, so we pad the image with a border on the left and right
            self.border_x = (self.content_height * viewport_ratio) - self.content_width
            self.border_y = 0
        else:
            # viewport is taller than image, so we pad the image with a border on the top and bottom
            # note: it is possible that both borders are zero
            self.border_y = (self.content_width / viewport_ratio) - self.content_height
            self.border_x = 0
        print(f"update_content_pos_and_scale2: {self.border_x} {self.border_y}")

        minscale = min(self.viewport_width / (self.content_width + self.border_x), self.viewport_height / (
                    self.content_height + self.border_y))  # we can't zoom out more than the full image in the viewport
        if self.scale is None:
            self.scale = self.start_scale if self.start_scale is not None else minscale  # start_scale is the preferred value, but if it is None, we use the fully zoomed out
        self.scale = self.clamp(self.scale, max(minscale, self.min_scale), self.max_scale)

        print(
            f"update_content_pos_and_scale3: {self.scale} {self.previous_scale} {minscale} {self.min_scale} {self.max_scale}")

        stack_width = (self.content_width + self.border_x) * self.scale  # the width of the full content scaled including the border
        stack_height = (self.content_height + self.border_y) * self.scale  # the height of the full content scaled including the border
        stack_overflow_x = max(stack_width - self.viewport_width,0)  # the amount of pixels that are outside the viewport for the stack (the range of offset_x)
        stack_overflow_y = max(stack_height - self.viewport_height,0)  # the amount of pixels that are outside the viewport for the stack (the range of offset_y)

        content_overflow_x = max(self.content_width * self.scale - self.viewport_width,0)
        # the amount of content pixels that are outside the viewport (the range of offset_x)
        content_overflow_y = max(self.content_height * self.scale - self.viewport_height,0)  # the amount of content pixels that are outside the viewport (the range of offset_y)

        print(f"update_content_pos_and_scale4: {stack_width} {stack_height} {stack_overflow_x} {stack_overflow_y}")
        if self.scale != self.previous_scale:
            if self.zoom_x is not None and self.innerstack.width is not None:
                # we have a zoom point, so we want to zoom in on that point (where the mouse is when zooming)
                # we calculate the amount of size change and then adjust the offsets to match the zoom point to the same position in the new image
                prevstack_width = (self.content_width + self.border_x) * self.previous_scale
                prevstack_height = (self.content_height + self.border_y) * self.previous_scale
                size_delta_x = stack_width - prevstack_width
                size_delta_y = stack_height - prevstack_height
                of_x = size_delta_x * (self.zoom_x / self.innerstack.width)  # offset of offset_x
                of_y = size_delta_y * (self.zoom_y / self.innerstack.height)  # offset of offset_y
                self.offset_x -= of_x  # offset is negative or zero since 0,0 is top left and we want to move the content to the left and up only
                self.offset_y -= of_y
                print(
                    f"update_content_pos_and_scale5: {self.offset_x} {self.offset_y} {of_x} {of_y} {size_delta_x} {size_delta_y} {self.zoom_x} {self.zoom_y} {self.innerstack.width} {self.innerstack.height}")
                self.zoom_x = None
                self.zoom_y = None
            self.previous_scale = self.scale

        # Let's figure out the valid range for offset_x and offset_y
        # Both are negative numbers since we are aiming with the top left corner outside the viewport
        # We have to aim the whole stack, not just the content
        # We know the movement range, which is content_overflow_x and content_overflow_y
        # If a content is smaller than the viewport, we want to center it (so we will use half of stack_overflow to center it)
        # But when there is no border then we don't want to center it, so half of stack_overflow is not correct

        balance_x = min(stack_overflow_x / 2, self.border_x * self.scale / 2)
        balance_y = min(stack_overflow_y / 2, self.border_y * self.scale / 2)
        self.offset_x = self.clamp(self.offset_x, -content_overflow_x - balance_x, -balance_x)
        self.offset_y = self.clamp(self.offset_y, -content_overflow_y - balance_y, -balance_y)
        print(
            f"update_content_pos_and_scale_: x{self.offset_x:.2f}y{self.offset_y} hb x{balance_x:.2f}y{balance_y:.2f} sox{stack_overflow_x:.2f}y{stack_overflow_y:.2f} soxx{content_overflow_x:.2f}yy{content_overflow_y:.2f}")
        self.inner_content.width = self.content_width * self.scale
        self.inner_content.height = self.content_height * self.scale
        # TODO In theory, using scale would be enough and might even scale text better than using width and height
        # But scaling had strange artifacts, and strange offsets with strange overlays and erratic behaviour
        #self.inner_content.offset = ft.Offset(x=-0.0, y=-0.0)
        #self.inner_content.scale = self.scale

        self.innerstack.width = stack_width
        self.innerstack.height = stack_height
        self.content_with_padding.width = stack_width
        self.content_with_padding.height = stack_height
        self.innerstack.left = self.offset_x
        self.innerstack.top = self.offset_y
        print(
            f"update_content_pos_and_scale6: (innerstack w{self.innerstack.width:.2f} h{self.innerstack.height:.2f} x{self.innerstack.left:.2f} y{self.innerstack.top:.2f})"
            f" scale{self.scale:.2f} (content w{self.content_width:.2f} h{self.content_height:.2f})")
        self.innerstack.update()

    def content_resize(self, event: ft.canvas.CanvasResizeEvent):
        print(f"content resize: {event.width} {event.height}")
        self.viewport_width = event.width
        self.viewport_height = event.height
        self.reset_content_dimensions()

    def on_pan_update(self, event: ft.DragUpdateEvent):
        print(f"pan update: {event.delta_x}, {event.delta_y}")
        self.offset_x += event.delta_x
        self.offset_y += event.delta_y
        self.update_content_pos_and_scale()
        if self.on_pan_update_callback is not None:
            self.on_pan_update_callback(event)

    def on_scroll_update(self, event: ft.ScrollEvent):
        self.scale = self.scale * (1 + (event.scroll_delta_y * self.scroll_to_scale_factor))
        self.zoom_x = event.local_x
        self.zoom_y = event.local_y
        print(
            f'scroll update: {self.innerstack.width} {event.scroll_delta_y} {self.scale}')
        self.update_content_pos_and_scale()
        if self.on_scroll_callback is not None:
            self.on_scroll_callback(event)

    def clamp(self, value: float, min: float, max: float) -> float:
        return min if value < min else max if value > max else value

    def click_content(self, event: ft.ControlEvent):
        print(f"click on overview image: {event.local_x} {event.local_y}")
        # we don't need to handle offset_x and offset_y since the coordinates are relative to the control which has been offset already
        x = (event.local_x) / self.scale - self.border_x / 2
        y = (event.local_y) / self.scale - self.border_y / 2
        print(f"click on overview image x: {event.local_x} {self.offset_x} {self.scale:.2f} {self.border_x} {x}")
        print(f"click on overview image y: {event.local_y} {self.offset_y} {self.scale:.2f} {self.border_y} {y}")
        if self.on_click_callback is not None:
            if 0<= x < self.content_width and 0 <= y < self.content_height:
                event.local_x = x
                event.local_y = y
                self.on_click_callback(event)

