
import discord
from discord.ext import commands
import json
import os
import random
from discord.ext.commands import cooldown, BucketType

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load atau buat database koin
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        data = json.load(f)
else:
    data = {}

def simpan():
    with open("data.json", "w") as f:
        json.dump(data, f)

def update_leaderboard_cache():
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    top_users = []
    for i, (user_id, koin) in enumerate(sorted_data[:10], start=1):
        top_users.append((user_id, koin))
    return top_users

leaderboard_cache = update_leaderboard_cache()

@bot.event
async def on_ready():
    print(f"Bot aktif sebagai {bot.user}")

@bot.command()
async def saldo(ctx):
    user_id = str(ctx.author.id)
    koin = data.get(user_id, 0)
    await ctx.send(f"\U0001F4B0 {ctx.author.mention}, kamu punya **{koin} koin**.")

@bot.command()
@commands.has_permissions(administrator=True)
async def tambah(ctx, member: discord.Member, jumlah: int):
    user_id = str(member.id)
    data[user_id] = data.get(user_id, 0) + jumlah
    simpan()
    global leaderboard_cache
    leaderboard_cache = update_leaderboard_cache()
    await ctx.send(f"\u2705 {jumlah} koin ditambahkan untuk {member.mention}!")

@bot.command()
async def tukar(ctx):
    user_id = str(ctx.author.id)
    koin = data.get(user_id, 0)
    harga = 100  # harga akses role

    if koin < harga:
        await ctx.send("\u274C Koin kamu belum cukup untuk menukar role.")
        return

    role_id = 1388716314872516659

    data[user_id] -= harga
    simpan()
    global leaderboard_cache
    leaderboard_cache = update_leaderboard_cache()

    role = ctx.guild.get_role(role_id)
    await ctx.author.add_roles(role)

    await ctx.send(f"\u2705 {ctx.author.mention}, kamu berhasil menukar {harga} koin dan mendapatkan role **{role.name}**!")

class SlotView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author

    @discord.ui.button(label="Main Lagi", style=discord.ButtonStyle.primary)
    async def main_lagi(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Ini bukan tombol kamu!", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        symbols = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎"]
        slot_result = [random.choice(symbols) for _ in range(3)]
        hasil = " ".join(slot_result)

        if slot_result[0] == slot_result[1] == slot_result[2]:
            koin_menang = random.randint(50, 150)
            data[user_id] = data.get(user_id, 0) + koin_menang
            simpan()
            global leaderboard_cache
            leaderboard_cache = update_leaderboard_cache()
            await interaction.response.edit_message(content=f"🎰 | {hasil}\n🎉 {interaction.user.mention}, kamu MENANG dan dapat **{koin_menang} koin**!", view=self)
        else:
            await interaction.response.edit_message(content=f"🎰 | {hasil}\n💥 {interaction.user.mention}, kamu zonk! Coba lagi nanti!", view=self)

@bot.command()
@cooldown(1, 10, BucketType.user)
async def main(ctx):
    user_id = str(ctx.author.id)
    symbols = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎"]
    slot_result = [random.choice(symbols) for _ in range(3)]
    hasil = " ".join(slot_result)
    view = SlotView(ctx.author)

    if slot_result[0] == slot_result[1] == slot_result[2]:
        koin_menang = random.randint(50, 150)
        data[user_id] = data.get(user_id, 0) + koin_menang
        simpan()
        global leaderboard_cache
        leaderboard_cache = update_leaderboard_cache()
        await ctx.send(f"🎰 | {hasil}\n🎉 {ctx.author.mention}, kamu MENANG dan dapat **{koin_menang} koin**!", view=view)
    else:
        await ctx.send(f"🎰 | {hasil}\n💥 {ctx.author.mention}, kamu zonk! Coba lagi nanti!", view=view)

@main.error
async def main_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"\u23F3 {ctx.author.mention}, tunggu {round(error.retry_after, 1)} detik sebelum bermain lagi!")

@bot.command()
async def leaderboard(ctx):
    if not leaderboard_cache:
        await ctx.send("Belum ada data koin.")
        return

    embeds = []
    for i, (user_id, koin) in enumerate(leaderboard_cache[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        badge = " 🥇 TOP PLAYER" if i == 1 else ""
        embed = discord.Embed(
            title=f"#{i} {user.name}{badge}",
            description=f"🪙 **{koin} koin**",
            color=discord.Color.gold() if i == 1 else discord.Color.blurple()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embeds.append(embed)

    for embed in embeds:
        await ctx.send(embed=embed)

import os
bot.run(os.getenv("DISCORD_TOKEN"))
