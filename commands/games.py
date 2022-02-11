import logging
import random

import discord
from discord import Option
from discord.commands import slash_command
from discord.ext import commands

from core.text.yuzuru_embed import YuzuruEmbed
from core.yuzuru_bot import YuzuruContext
from database.models.db_models import User, GambleHistory

logger = logging.getLogger(__name__)

dice_std_win_multiplier = 2
dice_exact_win_multiplier = 4
dice_outcomes = ['higher than 7', 'lower than 7', 'exactly 7']
dice_std_win_responses = ['Nice, you guessed correctly!', "Wow, you're a wizard!", 'How are you so good at this?!',
                          'Way to go!', 'Nice guess!']
dice_exact_win_responses = ['Alright, who gave you the crystal ball?', "Wow!! Either you're psychic or really lucky!",
                            "Excellent!! You got it exactly right!"]
dice_loss_responses = ['Aw, better luck next time.', 'Nice try!', 'Drat, you lost.',
                       "I'm gonna run out of room to put all these spirits!"]


def get_dice_options(ctx: YuzuruContext):
    return [x for x in dice_outcomes if x.startswith(ctx.value.lower())]


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(guild_ids=[931367517564317707])
    async def dice(self, ctx: YuzuruContext, spirits: int,
                   action: Option(str, "Will the outcome be higher, lower, or exactly seven?",
                                  autocomplete=get_dice_options)):
        """Play the dice game, betting on the outcome of two dice rolls."""
        f"""
        --- Dice Game Rules ---
        - Two six-sided die are rolled, the sum is the outcome.
        - Player bets on outcome being higher, lower, or equal to 7.
        - /roll 500 higher -- User is betting 500 spirits that the outcome is higher than 7.
        - Higher and lower pay {dice_std_win_multiplier}x, "7" pays {dice_exact_win_multiplier}x on a win.
        - Losses pay 0x.        
        """
        user, created = User.get_or_create(user_id=ctx.user.id)

        if action not in dice_outcomes:
            await ctx.respond('Please select a proper prediction from the context menu.')
            return

        if spirits < 50:
            await ctx.respond('You need to bet at least 50 spirits to play.')
            return

        if user.spirits < spirits:
            await ctx.respond(f'You only have {user.spirits} spirits (bet amount: {spirits}). '
                              f'Go get some more from `/daily`!', ephemeral=True)
            return

        # First thing, take away spirits
        user.spirits -= spirits

        d1 = random.randint(1, 7)
        d2 = random.randint(1, 7)
        outcome = d1 + d2

        payout_multiplier = 0
        winning_selection = None
        if outcome > 7:
            winning_selection = dice_outcomes[0]
        elif outcome < 7:
            winning_selection = dice_outcomes[1]
        elif outcome == 7:
            winning_selection = dice_outcomes[2]
            payout_multiplier = dice_exact_win_multiplier

        if winning_selection == action:
            # User won
            user.spirits += spirits * payout_multiplier

            if payout_multiplier == dice_std_win_multiplier:
                statement = random.choice(dice_std_win_responses)
            elif payout_multiplier == dice_exact_win_multiplier:
                statement = random.choice(dice_exact_win_responses)
            else:
                logger.warning(f'Dice fallback winning response used instead of dynamic choices -- something is wrong!')
                statement = 'Nice, you won!'

            gh = GambleHistory(game='dice', win=True, bet=spirits, payout_multiplier=payout_multiplier)
            gh.save()

            embed = YuzuruEmbed()
            embed.color = discord.Color.green()
            if payout_multiplier == dice_exact_win_multiplier:
                embed.color = discord.Color.gold()

            embed.description = f'{statement}\n🎲 {d1} 🎲 {d2} = 🎲🎲 {outcome} (Prediction: {action})\n' \
                                f'Payout: `{payout_multiplier}x`: +{spirits * payout_multiplier}'
            embed.set_footer(text=f'You now have {user.spirits} spirits.')
            await ctx.respond(embed=embed)
        else:
            # User lost
            gh = GambleHistory(game='dice', bet=spirits)
            gh.save()

            statement = random.choice(dice_loss_responses)

            embed = YuzuruEmbed()
            embed.color = discord.Color.red()
            embed.description = f'{statement}\n🎲 {d1} + 🎲 {d2} = 🎲🎲 {outcome} (Prediction: {action})'
            embed.set_footer(text=f'You now have {user.spirits} spirits.')
            await ctx.respond(embed=embed)

        user.save()


def setup(bot):
    bot.add_cog(Games(bot))
