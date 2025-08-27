import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
import string
from PIL import Image, ImageDraw, ImageFont
import io
import asyncio

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
VERIFICATION_CHANNEL_ID = int(os.getenv('VERIFICATION_CHANNEL_ID'))
UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID'))
WHITELISTED_GUILD_ID = int(os.getenv('WHITELISTED_GUILD_ID'))
OWNER_ID = int(os.getenv('OWNER_ID', '0'))  

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

pending_verifications = {}

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label='🔒 Verify', style=discord.ButtonStyle.red, custom_id='verify_button')
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_verification(interaction)

def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) # k=69420 x.y.z 
    
    width, height = 200, 80
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 30)
    except:
        font = ImageFont.load_default()
    
    for _ in range(5):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='red', width=2)
    
    text_width = draw.textlength(captcha_text, font=font)
    x = (width - text_width) // 2
    y = (height - 30) // 2
    
    draw.text((x, y), captcha_text, fill='black', font=font)
    
    for _ in range(20):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point((x, y), fill='gray')
    
    return image, captcha_text

async def handle_verification(interaction: discord.Interaction):
    user = interaction.user
    guild = interaction.guild
    
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    if verified_role in user.roles:
        await interaction.response.send_message("You are already verified!", ephemeral=True)
        return
    
    captcha_image, captcha_text = generate_captcha()
    img_bytes = io.BytesIO()
    captcha_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    pending_verifications[user.id] = captcha_text.lower()
    embed = discord.Embed(
        title="Xaint antirobots",
        description="Please solve the captcha below to get verified.\n\n**Instructions:**\n• Look at the image below\n• Type the 4 characters you see\n• You have 5 minutes to complete this",
        color=0xa40000
    )
    embed.set_footer(text="This captcha will expire in 5 minutes")
    try:
        file = discord.File(img_bytes, filename='captcha.png')
        embed.set_image(url="attachment://captcha.png")
        await user.send(embed=embed, file=file)
        await interaction.response.send_message("I've sent you a captcha in your DMs! Please check your direct messages.", ephemeral=True)
        await asyncio.sleep(300)  # 5 mins 
        if user.id in pending_verifications:
            del pending_verifications[user.id]
            try:
                await user.send("Your verification captcha has expired. Please try again.")
            except:
                pass
                
    except discord.Forbidden:
        await interaction.response.send_message("I couldn't send you a DM! Please enable DMs from server members and try again.", ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    bot.add_view(VerifyView())
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_guild_join(guild):
    if guild.id != WHITELISTED_GUILD_ID:
        print(f'a random ass server added me? fuck it.: {guild.name} (ID: {guild.id})')
        try:
            if guild.system_channel:
                embed = discord.Embed(
                    title="Unauthorized Server",
                    description="This bot is only authorized for specific servers. Leaving now.",
                    color=0xa40000
                )
                await guild.system_channel.send(embed=embed)
        except:
            pass
        
        await guild.leave()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.DMChannel) and message.author.id in pending_verifications:
        user_answer = message.content.strip().lower()
        correct_answer = pending_verifications[message.author.id]
        
        if user_answer == correct_answer:
            del pending_verifications[message.author.id]
            guild = bot.get_guild(WHITELISTED_GUILD_ID)
            if guild:
                member = guild.get_member(message.author.id)
                if member:
                    verified_role = guild.get_role(VERIFIED_ROLE_ID)
                    unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)
                    
                    try:
                        if verified_role:
                            await member.add_roles(verified_role)
                        if unverified_role and unverified_role in member.roles:
                            await member.remove_roles(unverified_role)
                        
                        embed = discord.Embed(
                            title="Verification Successful!",
                            description="You have been successfully verified! You now have access to the server.",
                            color=0xa40000
                        )
                        await message.channel.send(embed=embed)
                        
                    except discord.Forbidden:
                        await message.channel.send("I don't have permission to assign roles. Please contact an administrator.")
                else:
                    await message.channel.send("You're not in the server anymore!")
            else:
                await message.channel.send("Server not found!")
        else:
            embed = discord.Embed(
                title="Incorrect Captcha",
                description="The captcha answer is incorrect. Please try the verification process again in the server.",
                color=0xa40000
            )
            await message.channel.send(embed=embed)
            del pending_verifications[message.author.id]
    
    await bot.process_commands(message)
# if youre lazy to put the damn chanel id then use this command xd
@bot.command(name='sendembed')
async def send_embed(ctx, channel_id: int = None):
    if ctx.author.id != OWNER_ID:
        return
    if channel_id is None:
        await ctx.send("Please provide a channel ID: `$sendembed <channel_id>`")
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("Channel not found!")
        return

    embed = discord.Embed(
        title="Xaint antirobots",
        description="Welcome to the server! To gain access to all channels, please complete the verification process\n\n**How to verify:**\n• Click the Verify button below\n• Solve the captcha sent to your DMs\n• Get verified and enjoy the server!\n\n**Note:** Make sure your DMs are open to receive the captcha.",
        color=0xa40000
    )
    embed.add_field(
        name="Why do we need verification?",
        value="Cuz the server owner dont like robo and some random braindead kid",
        inline=False
    )
    embed.set_footer(text="Click the button below to start verification")
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    view = VerifyView()
    await channel.send(embed=embed, view=view)
    await ctx.send(f"Verification embed sent to {channel.mention}!")

@send_embed.error
async def send_embed_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Invalid channel ID! Please provide a valid number.")
    else:
        await ctx.send(f"An error occurred: {error}")
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN not found in .env file!")
    elif OWNER_ID == 0:
        print("Warning: OWNER_ID not set in .env file. The $sendembed command won't work!")
        bot.run(DISCORD_TOKEN)
    else:
        bot.run(DISCORD_TOKEN)