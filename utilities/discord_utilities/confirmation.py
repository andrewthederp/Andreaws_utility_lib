import typing

import discord


class Confirm(discord.ui.View):
    def __init__(self,
                 *,
                 user: typing.Union[discord.User, discord.Member],
                 timeout: int = None,
                 yes_callback: callable = None,
                 no_callback: callable = None
                 ):
        super().__init__(timeout=timeout)
        self.user = user
        self.answer = None

        self.yes_callback = yes_callback
        self.no_callback = no_callback

    async def interaction_check(self, interaction):
        return interaction.user == self.user

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        self.answer = True

        if self.yes_callback:
            await self.yes_callback(interaction, button)
        else:
            await interaction.message.delete()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        self.answer = False

        if self.no_callback:
            await self.no_callback(interaction, button)
        else:
            await interaction.message.delete()
