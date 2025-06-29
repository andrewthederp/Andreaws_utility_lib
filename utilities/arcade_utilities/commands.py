import arcade
import arcade.gui

from utilities.commands import get_command_list


class CommandView(arcade.gui.UIView):
    def __init__(self, background_view: arcade.View):
        super().__init__()
        self.background_view = background_view

        grid = arcade.gui.UIGridLayout(
            size_hint=(1, 1),
            column_count=1,
            row_count=2
        )
        grid.with_padding(all=50)
        grid.with_background(color=arcade.types.Color.from_iterable((0, 0, 0, 150)))
