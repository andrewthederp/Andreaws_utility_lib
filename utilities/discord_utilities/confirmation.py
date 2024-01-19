import discord

class Confirm(discord.ui.View):
    def __init__(self, *, user, timeout=None):
        super().__init__(timeout=timeout)
        self.user = user
        self.answer = None

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, _: discord.Button):
        self.stop()
        self.answer = True

        await interaction.message.delete()

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, _: discord.Button):
        self.stop()
        self.answer = False

        await interaction.message.delete()
