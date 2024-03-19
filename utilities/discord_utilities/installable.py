from discord.app_commands import MissingApplicationID, CommandSyncFailure, AppCommand
from discord import HTTPException


class InstallContext:
    def __new__(cls, *, guilds=False, users=False):
        value = []
        if guilds:
            value.append(0)
        if users:
            value.append(1)
        return value


class Context:
    def __new__(cls, *, guilds=False, bot_dm=False, private_channel=False):
        value = []
        if guilds:
            value.append(0)
        if bot_dm:
            value.append(1)
        if private_channel:
            value.append(2)
        return value


async def to_dict(command, *, do_translate=False):
    if do_translate:
        dct = await command.get_translated_payload(translator)
    else:
        dct = command.to_dict()

    if command.parent is None:
        dct["integration_types"] = command.extras.get("integration_types", [0])
        dct["contexts"] = command.extras.get("contexts", [0, 1, 2])

    return dct


async def magic_sync(tree):
    if tree.client.application_id is None:
        raise MissingApplicationID

    commands = tree._get_all_commands()

    translator = tree.translator
    if translator:
        payload = [await to_dict(command, do_translate=True) for command in commands]
    else:
        payload = [await to_dict(command) for command in commands]

    try:
        data = await tree._http.bulk_upsert_global_commands(tree.client.application_id, payload=payload)
    except HTTPException as e:
        if e.status == 400 and e.code == 50035:
            raise CommandSyncFailure(e, commands) from None
        raise

    return [AppCommand(data=d, state=tree._state) for d in data]
