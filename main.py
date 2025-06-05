import discord
import os
import re
import qrcode
import io
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables from .env file
load_dotenv()

# Get the token with a safer method
TOKEN = os.getenv('DISCORD_TOKEN')

# Configure intents
intents = discord.Intents.default()
intents.message_content = True  # Need message content intent to read messages

# Initialize bot with command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# URL regex pattern for finding URLs in messages
URL_PATTERN = re.compile(r'https?://\S+')

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    print(f'{bot.user.name} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_message(message):
    """Event triggered when a message is sent in a channel the bot can see."""
    # Don't respond to bot's own messages
    if message.author == bot.user:
        return

    # Check if message contains a URL
    urls = re.findall(URL_PATTERN, message.content)
    if urls:
        # Get the first URL
        url = urls[0]

        try:
            # Generate QR code
            qr_img = generate_qr_code(url)

            # Convert PIL Image to a file-like object
            with io.BytesIO() as image_binary:
                qr_img.save(image_binary, 'PNG')
                image_binary.seek(0)

                # Send QR code image as a response
                await message.channel.send(
                    f"QR Code for {url}",
                    file=discord.File(fp=image_binary, filename="qrcode.png")
                )
        except Exception as e:
            await message.channel.send(f"Error generating QR code: {str(e)}")

    # Process commands if any
    await bot.process_commands(message)

def generate_qr_code(text):
    """Generate a QR code from text."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white")

@bot.command(name='qr')
async def qr_command(ctx, *, url=None):
    """Command to generate QR code from provided URL."""
    if not url:
        await ctx.send("Please provide a URL. Usage: `!qr https://example.com`")
        return

    try:
        # Generate QR code
        qr_img = generate_qr_code(url)

        # Convert PIL Image to a file-like object
        with io.BytesIO() as image_binary:
            qr_img.save(image_binary, 'PNG')
            image_binary.seek(0)

            # Send QR code image as a response
            await ctx.send(
                f"QR Code for {url}",
                file=discord.File(fp=image_binary, filename="qrcode.png")
            )
    except Exception as e:
        await ctx.send(f"Error generating QR code: {str(e)}")

# Run the bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: Discord token not found. Make sure you have set the DISCORD_TOKEN environment variable.")
