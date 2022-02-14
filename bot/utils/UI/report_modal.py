from discord.ui import InputText, Modal
import discord


class ReportModal(Modal):
    def __init__(self, ctx, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        print(ctx.author.id)
        self.add_item(
            InputText(
                label="Report Reason",
                placeholder="What rule has this user broken?"
            ))

        self.add_item(
            InputText(
                label=f"Detailed Information (Optional)",
                placeholder="Go into detail about what this user has done that goes against our rules.",
                style=discord.InputTextStyle.long,
                max_length=1500,
                required=False
            )
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Your Modal Results", color=discord.Color.random())
        embed.add_field(name="Submitted By:", value=f"{interaction.user.id}")
        embed.add_field(name="Submitted By", value=self.children[0].value, inline=False)
        embed.add_field(name="Second Input", value=self.children[1].value, inline=False)
        await interaction.response.send_message(embeds=[embed])

