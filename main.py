
import os
import discord
import aiohttp
import datetime

from discord.ext import commands, tasks

# =====================================
# HARD TOWN RP - SERVER STATUS SYSTEM
# =====================================

# Secret Token
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

if not BOT_TOKEN:
    raise ValueError("DISCORD_TOKEN is missing!")

# Server Settings
SERVER_IP = "77.83.242.54"
SERVER_PORT = "30120"

SERVER_NAME = "Hard Town RP"
SERVER_SEASON = "Season 8"

# ضع رابط شعارك المباشر هنا
LOGO_URL = "https://example.com/logo.png"

UPDATE_SECONDS = 20

# =====================================
# BOT SETTINGS
# =====================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

status_message = None
start_time = datetime.datetime.now(
    datetime.timezone.utc
)

# =====================================
# GET FIVEM SERVER DATA
# =====================================

async def get_server_data():

    url = (
        f"http://{SERVER_IP}:{SERVER_PORT}"
        "/dynamic.json"
    )

    timeout = aiohttp.ClientTimeout(total=8)

    async with aiohttp.ClientSession(
        timeout=timeout
    ) as session:

        async with session.get(url) as response:

            response.raise_for_status()

            data = await response.json(
                content_type=None
            )

            return {
                "players": data.get("clients", 0),
                "max_players": data.get(
                    "sv_maxclients", 0
                )
            }


# =====================================
# CREATE STATUS EMBED
# =====================================

async def create_embed():

    uptime = (
        datetime.datetime.now(datetime.timezone.utc)
        - start_time
    )

    days = uptime.days

    hours, remainder = divmod(
        uptime.seconds, 3600
    )

    minutes, seconds = divmod(
        remainder, 60
    )

    try:

        data = await get_server_data()

        online = True
        players = data["players"]
        max_players = data["max_players"]

    except Exception as error:

        print(f"Server Error: {error}")

        online = False
        players = 0
        max_players = 0

    embed = discord.Embed(
        title="MTRP ™ | حالة السيرفر • Server Status",

        description=(
            f"**{SERVER_NAME} Cfw {SERVER_SEASON}**\n"
            "نظام تحديث حالة السيرفر تلقائياً\n\n"
            "تقديم | سيرفر رسمي"
        ),

        color=(
            discord.Color.green()
            if online
            else discord.Color.red()
        )
    )

    # STATUS

    embed.add_field(
        name="📊 Status | الحالة",

        value=(
            "🟢 Online"
            if online
            else "🔴 Offline"
        ),

        inline=False
    )

    # PLAYERS

    embed.add_field(
        name="👥 Players | اللاعبين",

        value=f"`{players} / {max_players}`",

        inline=False
    )

    # UPTIME

    embed.add_field(
        name="⏱️ Uptime | مدة التشغيل",

        value=(
            f"`{days} يوم و {hours} ساعة "
            f"و {minutes} دقيقة`"
        ),

        inline=False
    )

    # CONNECT

    embed.add_field(
        name="🔌 F8 Connect | أمر الاتصال",

        value=f"```connect {SERVER_IP}```",

        inline=False
    )

    # SERVER LOGO

    if LOGO_URL.startswith(("https://", "http://")):
        if "example.com" not in LOGO_URL:
            embed.set_image(url=LOGO_URL)

    # FOOTER

    embed.set_footer(
        text=f"MTO System • تحديث كل {UPDATE_SECONDS} ثانية"
    )

    return embed


# =====================================
# AUTOMATIC UPDATE
# =====================================

@tasks.loop(seconds=UPDATE_SECONDS)
async def update_status():

    global status_message

    if status_message is None:
        return

    embed = await create_embed()

    try:

        await status_message.edit(
            embed=embed
        )

    except discord.NotFound:

        status_message = None
        update_status.cancel()

    except discord.HTTPException as error:

        print(f"Discord Error: {error}")


@update_status.before_loop
async def before_update():

    await bot.wait_until_ready()


# =====================================
# STATUS COMMAND
# =====================================

@bot.command(name="status")
@commands.has_permissions(administrator=True)
async def status(ctx):

    global status_message

    embed = await create_embed()

    status_message = await ctx.send(
        embed=embed
    )

    if not update_status.is_running():
        update_status.start()


# =====================================
# COMMAND ERROR
# =====================================

@status.error
async def status_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):

        await ctx.send(
            "❌ هذا الأمر خاص بالإداريين."
        )

    else:

        print(f"Command Error: {error}")


# =====================================
# BOT READY
# =====================================

@bot.event
async def on_ready():

    print("==============================")
    print(f"Bot Online: {bot.user}")
    print("Hard Town Status System Started")
    print("==============================")


# =====================================
# RUN BOT
# =====================================

bot.run(BOT_TOKEN)
