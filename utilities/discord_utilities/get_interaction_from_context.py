import discord
from discord.ext import commands
import datetime


class InteractionResponse:
    def __init__(self, inter, context):
        self.inter = inter
        self.context = context

    @staticmethod
    def is_done():
        return False

    async def defer(self):
        pass

    async def send_message(self, *args, **kwargs):
        self.inter.message = await self.context.send(*args, **kwargs)

    async def edit_message(self, *args, **kwargs):
        await self.inter.message.send(*args, **kwargs)

    async def send_modal(self, modal):
        raise Exception("This is a fake interaction object, it can't send a modal.")


class Interaction:
    def __init__(self, context: commands.Context):
        self.user = context.author
        self.guild = context.guild
        if context.guild:
            self.guild_id = context.guild
            self.app_permissions = context.channel.permissions_for(context.guild.me)
        else:
            self.guild_id = None
            self.app_permissions = discord.Permissions(180224)
        self.application_id = context.bot.application_id
        self.channel = context.channel
        self.channel_id = context.channel.id
        self.client = context.bot
        self.command = context.command

        self.type = -1
        self.token = ""
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.command_failed = False
        self.data = {}
        self.extras = {}
        self.message = None

        self.response = InteractionResponse(self, context)
        self.followup = ...

    @staticmethod
    def is_expired():
        return False

    async def delete_original_response(self):
        if self.message:
            await self.message.delete()

    async def edit_original_response(self, **kwargs):
        if self.message:
            await self.message.edit(**kwargs)

    async def original_response(self):
        return self.message
