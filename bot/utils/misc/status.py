from random import choice


def get_status(guild, yt):
    channel = yt.channels().list(
        part="statistics",
        id="UCB5dggJv599ioXUL11d0LXg"
    ).execute()
    statistics = channel["items"][0]["statistics"]
    name = choice(guild.get_role(893933214656233563).members).display_name
    statuses = [
        f"Thank you to the {statistics.get('subscriberCount', 'ERROR')} people subscribed to Sykese",
        f"Sykese currently has {statistics.get('videoCount', 'ERROR')} videos",
        f"{int((int(statistics.get('subscriberCount', 0))/30_000)*100)}% to 30,000 subscribers",
        f"Thank you for boosting {name}!",
        "Blue is the best color",
        f"Hello {name}, thanks for being in our server",
        "Want to check your server level? Use the `/profile` command",
        "Want to see where you rank amongst your fellow server members? Use the `/level_leaderboard` command",
        "Follow Sykese on the forums to help him become the most followed user on the site"
    ]
    return choice(statuses)
