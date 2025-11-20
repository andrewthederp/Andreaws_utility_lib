import typing

import discord


# I plan to deprecate this class
class MakeModal(discord.ui.Modal):
    def __init__(self,
                 *,
                 title: str,
                 callback: callable,
                 inputs: typing.List[typing.Union[dict, discord.ui.TextInput]]
                 ):
        super().__init__(title=title)

        for text_input_data in inputs:
            if isinstance(text_input_data, dict):
                text_input = discord.ui.TextInput(
                    placeholder=text_input_data["placeholder"],
                    required=text_input_data.get("required", False),
                    style=text_input_data.get("style", discord.TextStyle.short),
                    default=text_input_data.get('default')
                )

                self.add_item(
                    discord.ui.Label(
                        text=text_input_data["label"],
                        description=text_input_data.get("description"),
                        component=text_input
                    )
                )
            elif isinstance(text_input_data, discord.ui.Label):
                self.add_item(text_input_data)

        self.on_submit_func = callback

    async def on_submit(self, interaction: discord.Interaction):
        values = {}

        for item in self.children:
            if isinstance(item, discord.ui.Label):
                values[item.label.lower()] = item.component.value

        await self.on_submit_func(interaction, values)
