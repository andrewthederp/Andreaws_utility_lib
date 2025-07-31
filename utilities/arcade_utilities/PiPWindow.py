from pyglet.window import DefaultMouseCursor
import arcade
import pyglet
import enum


class DragRectType(enum.IntFlag):
    MOVEABLE           = 0
    RESIZE_TOP         = enum.auto()
    RESIZE_BOTTOM      = enum.auto()
    RESIZE_LEFT        = enum.auto()
    RESIZE_RIGHT       = enum.auto()

    RESIZE_TOPLEFT     = RESIZE_TOP    | RESIZE_LEFT
    RESIZE_TOPRIGHT    = RESIZE_TOP    | RESIZE_RIGHT
    RESIZE_BOTTOMRIGHT = RESIZE_BOTTOM | RESIZE_RIGHT
    RESIZE_BOTTOMLEFT  = RESIZE_BOTTOM | RESIZE_LEFT


class DragRect:
    def __init__(self, rect: arcade.Rect, type: DragRectType, cursor: str | pyglet.window.MouseCursor | None = None):
        self.type = type

        self.left = rect.left
        self.bottom = rect.bottom
        self.width = rect.width
        self.height = rect.height

        self._cursor = cursor

    def __repr__(self):
        return f"<DragRect type={self.type.name} rect={self.rect}>"

    @property
    def cursor(self):
        if isinstance(self._cursor, pyglet.window.MouseCursor):
            return self._cursor

        window = arcade.get_window()
        return window.get_system_mouse_cursor(self._cursor)  # type: ignore

    @property
    def rect(self):
        return arcade.LBWH(self.left, self.bottom, self.width, self.height)


class PiPWindow(arcade.Window):
    def __init__(self, minimum_size: tuple[float, float] | arcade.Vec2, *args, **kwargs):
        super().__init__(*args, **kwargs, style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
        self.drag_rects = self.make_drag_rects()
        self.minimum_size = arcade.Vec2(*minimum_size)

        self.dragging: DragRect | None = None
        self.last_mouse_pos: tuple[int, int] = (-1, -1)
        self.cursor = DefaultMouseCursor()  # default cursor

        screen = arcade.get_screens()[0]  # not sure if this can cause issues with multi-moniter setups since I don't have a multi-moniter setup
        mode = screen.get_mode()
        self.sw, self.sh = mode.width, mode.height

    def resized(self):
        pass

    def make_drag_rects(self) -> list[DragRect]:
        w, h = self.size
        margin = 10

        return [
            DragRect(rect=arcade.LBWH(0, h - margin, margin, margin), type=DragRectType.RESIZE_TOPLEFT, cursor=self.CURSOR_SIZE_UP_LEFT),
            DragRect(rect=arcade.LBWH(margin, h - margin, w - (margin * 2), margin), type=DragRectType.RESIZE_TOP, cursor=self.CURSOR_SIZE_UP),
            DragRect(rect=arcade.LBWH(w - margin, h - margin, margin, margin), type=DragRectType.RESIZE_TOPRIGHT, cursor=self.CURSOR_SIZE_UP_RIGHT),

            DragRect(rect=arcade.LBWH(0, margin, margin, h - (margin * 2)), type=DragRectType.RESIZE_LEFT, cursor=self.CURSOR_SIZE_LEFT),
            DragRect(rect=arcade.LBWH(w - margin, margin, margin, h - (margin * 2)), type=DragRectType.RESIZE_RIGHT, cursor=self.CURSOR_SIZE_RIGHT),

            DragRect(rect=arcade.LBWH(0, 0, margin, margin), type=DragRectType.RESIZE_BOTTOMLEFT, cursor=self.CURSOR_SIZE_DOWN_LEFT),
            DragRect(rect=arcade.LBWH(margin, 0, w - (margin * 2), margin), type=DragRectType.RESIZE_BOTTOM, cursor=self.CURSOR_SIZE_DOWN),
            DragRect(rect=arcade.LBWH(w - margin, 0, margin, margin), type=DragRectType.RESIZE_BOTTOMRIGHT, cursor=self.CURSOR_SIZE_DOWN_RIGHT),

            DragRect(rect=arcade.LBWH(margin, margin, w - (margin * 2), h - (margin * 2)), type=DragRectType.MOVEABLE, cursor=None)
        ]

    def on_update(self, _):  # can't use `on_mouse_drag` because shifting the screen position triggers the event (I think?)
        cx, cy = self.get_mouse_pos()
        x, y = self.last_mouse_pos
        self.last_mouse_pos = cx, cy

        if self.dragging is None:
            xy = self.mouse["x"], self.mouse["y"]  # type: ignore
            for rect in self.drag_rects:
                if rect.rect.point_in_rect(xy):
                    self.set_mouse_cursor(rect.cursor)
                    break
            else:
                self.set_mouse_cursor(self.cursor)

            return

        dx, dy = cx - x, cy - y

        if not (dx or dy):
            return

        ww, wh = self.size
        wx, wy = self.get_location()

        mw, mh = self.minimum_size

        match self.dragging.type:
            case DragRectType.MOVEABLE:
                self.set_location(int(wx + dx), int(wy + dy))
            case DragRectType.RESIZE_RIGHT:
                nw = max(ww + dx, mw)
                dx = int(nw - ww)
                self.set_size(ww + dx, wh)
            case DragRectType.RESIZE_BOTTOMRIGHT:
                nw, nh = max(ww + dx, mw), max(wh + dy, mh)
                dx, dy = int(nw - ww), int(nh - wh)
                self.set_size(ww + dx, wh + dy)
            case DragRectType.RESIZE_BOTTOM:
                nh =  max(wh + dy, mh)
                dy = int(nh - wh)
                self.set_size(ww, wh + dy)
            case DragRectType.RESIZE_BOTTOMLEFT:
                nw, nh = max(ww - dx, mw), max(wh + dy, mh)
                dx, dy = -int(nw - ww), int(nh - wh)
                self.set_size(ww - dx, wh + dy)
                self.set_location(wx + dx, wy)
            case DragRectType.RESIZE_LEFT:
                nw = max(ww - dx, mw)
                dx = -int(nw - ww)
                self.set_size(ww - dx, wh)
                self.set_location(wx + dx, wy)
            case DragRectType.RESIZE_TOPLEFT:
                nw, nh = max(ww - dx, mw), max(wh - dy, mh)
                dx, dy = -int(nw - ww), int(wh - nh)
                self.set_size(ww - dx, wh - dy)
                self.set_location(wx + dx, wy + dy)
            case DragRectType.RESIZE_TOP:
                nh = max(wh - dy, mh)
                dy = int(wh - nh)
                self.set_size(ww, wh - dy)
                self.set_location(wx, wy + dy)
            case DragRectType.RESIZE_TOPRIGHT:
                nw, nh = max(ww + dx, mw), max(wh - dy, mh)
                dx, dy = int(nw - ww), int(wh - nh)
                self.set_size(ww + dx, wh - dy)
                self.set_location(wx, wy + dy)

    def get_mouse_pos(self):
        "A function to get the mouse pos on the display, not the arcade window"

        ww, wh = self.size
        wx, wy = self.get_location()
        mx, my = self.mouse["x"], self.mouse["y"]  # type: ignore

        return int(mx + wx), int(wy + (wh - my))

    def on_mouse_press(self, x, y, button, _):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        for rect in self.drag_rects:
            if rect.rect.point_in_rect((x, y)):
                self.dragging = rect
                return

    def on_mouse_release(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT and self.dragging is not None:
            return

        self.resized()

        self.drag_rects = self.make_drag_rects()
        self.dragging = None
