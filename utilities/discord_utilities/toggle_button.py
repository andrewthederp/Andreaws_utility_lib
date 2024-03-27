import discord


class ToggleButton(discord.ui.Button):
    def __init__(self, *, styles, **kwargs):
        super().__init__(**kwargs, style=styles[False])

        self.state = False
        self.styles = styles

    async def after_callback(self, interaction):
        await interaction.response.edit_message(view=self.view)

    async def callback(self, interaction):
        self.state = not self.state
        self.style = self.styles[self.state]
        await self.after_callback(interaction)
