import discord

class MakeModal(discord.ui.Modal):
    def __init__(self, *, title, callback, inputs):
        super().__init__(title=title)

        for text_input_data in inputs:
            text_input = discord.ui.TextInput(
                label=text_input_data["label"],
                placeholder=text_input_data["placeholder"],
                required=text_input_data.get("required", False),
                style=text_input_data.get("style", discord.TextStyle.short),
                default=text_input_data.get('default')
            )
            self.add_item(text_input)

        self.on_submit_func = callback

    async def on_submit(self, interaction: discord.Interaction):
        values = {}

        for item in self.children:
            if isinstance(item, discord.ui.TextInput):
                values[item.label.lower()] = item.value

        await self.on_submit_func(interaction, values)
