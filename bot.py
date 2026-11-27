import discord
from discord.ext import commands
import dotenv
import asyncio
import os
import random

dotenv.load_dotenv()

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

class PrivateThreadCreate(discord.ui.Modal):
    def __init__(self) -> None:
        super().__init__(title="独り言スレッドを作成する", timeout=180)

        self.title_input = discord.ui.TextInput(label="タイトル", required=True)
        self.add_item(self.title_input)

        self.key_1 = random.randint(1, 9)
        self.key_2 = random.randint(1, 9)

        self.robot_check = discord.ui.TextInput(label=f"次の計算結果を入力してください: 「{self.key_1}+{self.key_2}」", required=True)
        self.add_item(self.robot_check)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if str(self.key_1 + self.key_2) != self.robot_check.value:
            await interaction.response.send_message(ephemeral=True, content=f"数字が正しく入力されていません。\n答え: 「{self.key_1+self.key_2}」")
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        thread = await interaction.channel.create_thread(
            name=self.title_input.value,
            type=discord.ChannelType.private_thread,
            invitable=True
        )

        asyncio.create_task(thread.add_user(interaction.user))
        asyncio.create_task(thread.add_user(discord.Object(1574720330579181608)))

        await interaction.followup.send(content=f"✅作成しました↓\n{thread.mention}", ephemeral=True)

        await thread.send(embed=discord.Embed(title="📢この独り言の説明", description="""この独り言スレッドは、
あなたとモデレーターのみが見ることができます。
""", color=discord.Color.blue()), view=discord.ui.View(timeout=None).add_item(discord.ui.Button(label="便利Botのご案内", url="https://canary.discord.com/channels/1575729780270301206/1575730744045867148")))

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.custom_id == "create-private-thread":
            await interaction.response.send_modal(PrivateThreadCreate())

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # 公開ひとりごと
    if message.channel.id == 1575732570132578349:
        if message.reference:
            await message.delete()

        return

@bot.event
async def on_ready():
    channel = bot.get_channel(1575733670571020399)

    await channel.purge(limit=10, check=lambda msg: msg.author.id == bot.user.id)

    await channel.send(
        view=discord.ui.View(timeout=None).add_item(discord.ui.Button(label="スレッドを作成する", custom_id="create-private-thread"))
    )

bot.run(os.environ.get('DISCORD_TOKEN'))