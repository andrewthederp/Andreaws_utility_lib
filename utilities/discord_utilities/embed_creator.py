import datetime

import discord
import copy

from .confirmation import Confirm
from .modal_creator import MakeModal
from .utils import get_image_url
from ..color_utilities import convert_to_color


class EmbedCreator(discord.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

        self.embed = discord.Embed(title='** **')

        self.current_embed_pos = 0
        self.embed_versions = [self.embed.copy()]

    async def edit_message(self, interaction):
        try:
            if not self.embed.fields:
                self.insert_field_at_button.disabled = True
                self.edit_field_button.disabled = True
                self.remove_field_at_button.disabled = True
                self.clear_all_fields_button.disabled = True
            else:
                self.insert_field_at_button.disabled = False
                self.edit_field_button.disabled = False
                self.remove_field_at_button.disabled = False
                self.clear_all_fields_button.disabled = False

            self.next_embed_button.disabled = True
            self.previous_embed_button.disabled = False
            await interaction.response.edit_message(embed=self.embed, view=self)
        except Exception as _:
            self.embed = self.embed_versions[-1]
            await interaction.response.send_message(content="Could not edit the embed", ephemeral=True)
            return False
        else:
            embed_amt = len(self.embed_versions)

            if self.current_embed_pos != embed_amt-1:
                print(self.embed_versions[:self.current_embed_pos])
                self.embed_versions = self.embed_versions[:self.current_embed_pos]

            self.current_embed_pos = len(self.embed_versions)

            dct = copy.deepcopy(self.embed.to_dict())
            embed = discord.Embed.from_dict(dct)

            self.embed_versions.append(embed)
            return True

    @discord.ui.button(label="Title", style=discord.ButtonStyle.blurple)
    async def title_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            title = values.get("title")

            self.embed.title = title

            await self.edit_message(inter)

        modal = MakeModal(
            title="Embed Title",
            callback=modal_callback,
            inputs=[
                {"label": "Title", "placeholder": "Embed title",
                 "default": None if self.embed.title in [None, '** **'] else self.embed.title}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Description", style=discord.ButtonStyle.blurple)
    async def description_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            description = values.get("description")

            self.embed.description = description

            await self.edit_message(inter)

        modal = MakeModal(
            title="Embed Description",
            callback=modal_callback,
            inputs=[
                {"label": "Description", "placeholder": "Embed description", "default": self.embed.description}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Color", style=discord.ButtonStyle.blurple)
    async def color_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            color = values.get("color")

            if color:
                r, g, b, _ = convert_to_color(color)
                color = discord.Color.from_rgb(r, g, b)
                self.embed.colour = color
            else:
                self.embed.colour = None

            await self.edit_message(inter)

        hex_color = convert_to_color(self.embed.colour.value, return_hex=True) if self.embed.color else ''

        modal = MakeModal(
            title="Embed Color",
            callback=modal_callback,
            inputs=[
                {"label": "Color", "placeholder": "Embed color", "default": hex_color}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Title url", style=discord.ButtonStyle.blurple)
    async def title_url_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            url = values.get("title url")

            if not url:
                self.embed.url = None
            elif url.startswith('http'):
                self.embed.url = url
            else:
                return await inter.response.send_message(content="That url is invalid", ephemeral=True)

            await self.edit_message(inter)

        modal = MakeModal(
            title="Embed Title Url",
            callback=modal_callback,
            inputs=[
                {"label": "Title Url", "placeholder": "Embed title url", "default": self.embed.url}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Timestamp", style=discord.ButtonStyle.blurple)
    async def timestamp_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            timestamp = values.get("timestamp")
            if timestamp:
                if timestamp.isdigit():
                    try:
                        self.embed.timestamp = datetime.datetime.fromtimestamp(int(timestamp))
                    except OSError:
                        return await inter.response.send_message(content="that is not a valid unix timestamp",
                                                                 ephemeral=True)
                else:
                    return await inter.response.send_message(content="The timestamp must be a unix timestamp",
                                                             ephemeral=True)
            else:
                self.embed.timestamp = None

            await self.edit_message(inter)

        modal = MakeModal(
            title="Embed Timestamp",
            callback=modal_callback,
            inputs=[
                {"label": "Timestamp", "placeholder": "Embed timestamp"}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Add field", style=discord.ButtonStyle.blurple, row=2)
    async def add_field_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            name = values["field name"]
            value = values["field value"]
            inline = bool(values.get("field inline"))

            if self.embed.title == "** **":
                self.embed.title = None

            self.embed.add_field(name=name, value=value, inline=inline)
            await self.edit_message(inter)

        modal = MakeModal(
            title="New field!",
            callback=modal_callback,
            inputs=[
                {"label": "Field name", "placeholder": "The name of the field", "required": True},
                {"label": "Field value", "placeholder": "The value of the field", "required": True},
                {"label": "Field inline", "placeholder": "Whether the field is inline or not (keep empty for false)"},
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Insert Field at", style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def insert_field_at_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            name = values["field name"]
            value = values["field value"]
            inline = bool(values.get("field inline"))

            try:
                position = int(values["field position"])
            except ValueError:
                return await inter.response.send_message("Invalid position", ephemeral=True)

            position -= 1

            try:
                self.embed.insert_field_at(position, name=name, value=value, inline=inline)
            except IndexError:
                return await inter.response.send_message("Invalid position", ephemeral=True)
            else:
                if self.embed.title == "** **":
                    self.embed.title = None

            await inter.response.edit_message(embed=self.embed, view=self)

        modal = MakeModal(
            title="Insert field",
            callback=modal_callback,
            inputs=[
                {"label": "Field position", "placeholder": "The position of where to insert the field",
                 "required": True},
                {"label": "Field name", "placeholder": "The name of the field", "required": True},
                {"label": "Field value", "placeholder": "The value of the field", "required": True},
                {"label": "Field inline", "placeholder": "Whether the field is inline or not (keep empty for false)"},
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Edit Field", style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def edit_field_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):

            try:
                position = int(values["field position"])
                position -= 1
            except ValueError:
                return await inter.response.send_message("Invalid position", ephemeral=True)

            field = self.embed.fields[position]

            name = values.get("field name") or field.name
            value = values.get("field value") or field.value
            inline = bool(values.get("field inline") or field.inline)

            try:
                self.embed.set_field_at(position, name=name, value=value, inline=inline)
            except IndexError:
                return await inter.response.send_message("Invalid position", ephemeral=True)
            else:
                if self.embed.title == "** **":
                    self.embed.title = None

            await self.edit_message(inter)

        modal = MakeModal(
            title="Edit field",
            callback=modal_callback,
            inputs=[
                {"label": "Field position", "placeholder": "The position of the field to edit", "required": True},
                {"label": "Field name", "placeholder": "The name of the field"},
                {"label": "Field value", "placeholder": "The value of the field"},
                {"label": "Field inline", "placeholder": "Whether the field is inline or not (keep empty for false)"},
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Remove field at", style=discord.ButtonStyle.red, row=2, disabled=True)
    async def remove_field_at_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            try:
                position = int(values["field position"])
            except ValueError:
                return await inter.response.send_message("Invalid position", ephemeral=True)

            try:
                self.embed.remove_field(position - 1)
            except IndexError:
                return await inter.response.send_message("Invalid position", ephemeral=True)

            if not self.embed:
                self.embed.title = "** **"

            await self.edit_message(inter)

        modal = MakeModal(
            title="Edit field",
            callback=modal_callback,
            inputs=[
                {"label": "Field position", "placeholder": "The position of the field to remove", "required": True}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Clear Fields", style=discord.ButtonStyle.red, row=2, disabled=True)
    async def clear_all_fields_button(self, interaction: discord.Interaction, _: discord.Button):
        view = Confirm(user=interaction.user)
        await interaction.response.send_message(content="Are you sure you want to clear all fields?", view=view,
                                                ephemeral=True)
        await view.wait()

        if view.answer:
            self.embed.clear_fields()
            if not self.embed:
                self.embed.title = "** **"
            await interaction.followup.edit_message(interaction.message.id, embed=self.embed, view=self)
            self.embed_versions.append(self.embed.copy())

    @discord.ui.button(label="Author", style=discord.ButtonStyle.blurple, row=3)
    async def author_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            name = values.get('author name')
            url = values.get('author url')
            icon_url = values.get('author icon url')

            if not name:
                self.embed.remove_author()
            else:
                self.embed.set_author(name=name, url=url, icon_url=get_image_url(inter, icon_url))

            await self.edit_message(inter)

        author = getattr(self.embed, '_author', {})

        modal = MakeModal(
            title="Embed author",
            callback=modal_callback,
            inputs=[
                {"label": "Author name", "placeholder": "Author name", "default": author.get("name")},
                {"label": "Author url", "placeholder": "Author url", "default": author.get("url")},
                {"label": "Author icon url", "placeholder": "Author icon url", "default": author.get("icon_url")}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.blurple, row=3)
    async def thumbnail_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            thumbnail_url = values.get('thumbnail url')
            self.embed.set_thumbnail(url=get_image_url(inter, thumbnail_url))
            await self.edit_message(inter)

        thumbnail = getattr(self.embed, '_thumbnail', {})

        modal = MakeModal(
            title="Embed thumbnail",
            callback=modal_callback,
            inputs=[
                {"label": "Thumbnail URL", "placeholder": "Thumbnail url", "default": thumbnail.get('url')}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Image", style=discord.ButtonStyle.blurple, row=3)
    async def image_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            image_url = values.get('image url')
            self.embed.set_image(url=get_image_url(inter, image_url))
            await self.edit_message(inter)

        image = getattr(self.embed, '_image', {})

        modal = MakeModal(
            title="Embed image",
            callback=modal_callback,
            inputs=[
                {"label": "Image URL", "placeholder": "Image url", "default": image.get('url')}
            ])

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.blurple, row=3)
    async def footer_button(self, interaction: discord.Interaction, _: discord.Button):
        async def modal_callback(inter, values):
            text = values.get('footer text')
            icon_url = values.get('footer icon url')

            self.embed.set_footer(text=text, icon_url=get_image_url(inter, icon_url))

            if not self.embed:
                self.embed.title = "** **"
            elif self.embed and self.embed.title == "** **":
                self.embed.title = None

            await self.edit_message(inter)

        footer = getattr(self.embed, '_footer', {})

        modal = MakeModal(
            title="Embed Footer",
            callback=modal_callback,
            inputs=[
                {"label": "Footer text", "placeholder": "Footer text", "default": footer.get("text")},
                {"label": "Footer Icon url", "placeholder": "Footer icon url", "default": footer.get("icon_url")}
            ])

        await interaction.response.send_modal(modal)


    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def previous_embed_button(self, interaction: discord.Interaction, _: discord.Button):
        self.current_embed_pos -= 1
        if self.current_embed_pos == 0:
            self.previous_embed_button.disabled = True
        self.next_embed_button.disabled = False

        self.embed = self.embed_versions[self.current_embed_pos]


        if not self.embed.fields:
            self.insert_field_at_button.disabled = True
            self.edit_field_button.disabled = True
            self.remove_field_at_button.disabled = True
            self.clear_all_fields_button.disabled = True
        else:
            self.insert_field_at_button.disabled = False
            self.edit_field_button.disabled = False
            self.remove_field_at_button.disabled = False
            self.clear_all_fields_button.disabled = False

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def next_embed_button(self, interaction: discord.Interaction, _: discord.Button):
        self.current_embed_pos += 1
        if self.current_embed_pos == len(self.embed_versions)-1:
            self.next_embed_button.disabled = True
        self.previous_embed_button.disabled = False

        self.embed = self.embed_versions[self.current_embed_pos]

        if not self.embed.fields:
            self.insert_field_at_button.disabled = True
            self.edit_field_button.disabled = True
            self.remove_field_at_button.disabled = True
            self.clear_all_fields_button.disabled = True
        else:
            self.insert_field_at_button.disabled = False
            self.edit_field_button.disabled = False
            self.remove_field_at_button.disabled = False
            self.clear_all_fields_button.disabled = False

        await interaction.response.edit_message(embed=self.embed, view=self)
