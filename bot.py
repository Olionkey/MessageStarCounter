import asyncio
import disputils
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
token = 'your token'


@bot.command()
@commands.max_concurrency(1, commands.BucketType.guild)
@commands.is_owner()
async def scan(ctx, emoji):
    result_dict = {}
    failed = []
    async with ctx.typing():
        for channel in ctx.guild.channels:
            if type(channel) is not discord.TextChannel:
                continue
            if not channel.permissions_for(ctx.guild.me).read_message_history:
                failed.append(channel.id)
                continue
            async for m in channel.history(limit=25000):
                result_dict.setdefault(m.author.id, 0)
                for r in m.reactions:
                    if r.emoji != emoji:
                        continue
                    result_dict[m.author.id] += r.count

        result_list = sorted(
            [
                [r, c] for r, c in result_dict.items()
            ], key=lambda l: l[1], reverse=True
        )

    all_users = []
    user_lookup = {}
    for u, _ in result_list:
        all_users.append(int(u))

    result = await ctx.guild.query_members(limit=None, user_ids=all_users)
    for r in result:
        user_lookup[r.id] = r

    p = commands.Paginator(prefix='', suffix='')
    for u, c in result_list:
        if c == 0:
            continue
        if u in user_lookup:
            un = str(user_lookup[u])
        else:
            un = "Deleted User"
        p.add_line(f"**{un}**: {c}")

    all_pages = [discord.Embed(
        title='Results',
        description=d
    ) for d in p.pages]

    paginator = disputils.EmbedPaginator(
        bot, all_pages
    )

    if failed != []:
        await ctx.send("some channels failed to scan")

    await paginator.run([ctx.message.author], ctx.channel)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} in {len(bot.guilds)} guilds!")


if __name__ == '__main__':
    bot.run(token)
