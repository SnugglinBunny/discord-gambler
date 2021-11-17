import discord
import discord.utils
from discord.ext import commands, tasks
from discord_gambler import _guild_id, _coinflip_channel
from decouple import config
from datetime import datetime

class CoinsTasks(commands.Cog):
    def __init__(self, bot):
        self._bot = bot
        self._economy = self._bot.get_cog("Economy")
        self._coinflip_cog = self._bot.get_cog("Coinflip")
        self.coins_reward_task.start()
        self.giveaway_jackpot.start()

    def cog_unload(self):
        self.coins_reward_task.cancel()
        self.giveaway_jackpot.cancel()

    @tasks.loop(seconds=10)
    async def coins_reward_task(self):
        if self.get_users_in_voice_channels():
            for member in self.get_users_in_voice_channels():
                self._economy.deposit(member, 50)

    @tasks.loop(seconds=30)
    async def giveaway_jackpot(self):
        if self._coinflip_cog._giveaway >= 50000:
            winner, percentage = self._coinflip_cog.run_giveaway()
            channel = discord.utils.get(self._bot.guild.channels, name=_coinflip_channel)
            await self._bot.get_channel(channel.id).send(
                embed=discord.Embed(
                    title="Information",
                    description=f"{winner.mention} has won the jackpot of {self._coinflip_cog._giveaway} with a {percentage} percent chance.",
                    color=discord.Color.green(),
                ), delete_after=30,
            )

    @coins_reward_task.before_loop
    async def before_coins_reward_task(self):
        await self._bot.wait_until_ready()

    @giveaway_jackpot.before_loop
    async def before_giveaway_jackpot(self):
        await self._bot.wait_until_ready()

    def get_users_in_voice_channels(self):
        active_members = []
        for channel in self._bot.get_guild(_guild_id).channels:
            if channel.type == discord.ChannelType.voice and len(channel.members) > 0:
                for member in channel.members:
                    active_members.append(member)
        return active_members
