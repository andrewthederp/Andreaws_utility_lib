import discord


class ToggleButton(discord.ui.Button):
    def __init__(self, *, styles=None, **kwargs):
        if styles is None:
            styles = {True: discord.ButtonStyle.blurple, False: discord.ButtonStyle.gray}

        super().__init__(**kwargs, style=styles[False])

        self.state = False
        self.styles = styles

    async def after_callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self.view)

    async def interaction_check(self, interaction: discord.Interaction):
        return True

    async def callback(self, interaction: discord.Interaction):
        if not self.interaction_check(interaction):
            return

        self.state = not self.state
        self.style = self.styles[self.state]
        await self.after_callback(interaction)
