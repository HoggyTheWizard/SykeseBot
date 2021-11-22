import discord

tag_list = {

    "sykese info": {
        "embedTitle": "Sykese FAQ",
        "embedDescription": "There are a lot of questions that get asked regarding Sykese, so here's a short list "
        "addressing the most common ones.",
        "embedColor": discord.Color.blue(),
        "fields": {
            1: {
                "name": "What is his username?",
                "value": "sykeseguy",
                "inline": False
            },
            2: {
                "name": "What is his favorite color?",
                "value": "Is that really a question you need to ask?",
                "inline": False
            },

            3: {
                "name": "Why don't you use your \"Sykese\" Minecraft account?",
                "value": "He lost access to it years ago.",
                "inline": False
            },
        }
    },

    "verify help": {
        "embedTitle": "Verification Help",
        "embedDescription": "It seems people tend to have certain difficulties when verifying. If this tag was called, "
                            "your issue will more than likely be resolved by following the instructions below.",
        "embedColor": discord.Color.blue(),
        "fields": {
            1: {
                "name": "Command Usage",
                "value": "+verify <Minecraft Username>. Yes, your __Minecraft__ username, not your Discord username. "
                         "We already have access to that.",
                "inline": False
            },
            2: {
                "name": "How do I verify?",
                "value": "Link your account to Hypixel, then run the command above. There is a gif pinned in the "
                         "verification channel demonstrating how to do this.",
                "inline": False
            },
            3: {
                "name": "My current account doesn't match my linked account? What does that mean?",
                "value": "Your linked account does not match with the account you are currently using. To resolve this,"
                " you either need to update your linked account on Hypixel or change your Discord account to match the "
                "linked one. Note that your account does not need to match after the verification process is over.",
                "inline": False
            },

            4: {
                "name": "I can't access Hypixel due to my account being banned. What do I do?",
                "value": "We do not have an automatic verification system for users who cannot log into Hypixel. "
                "Rather, you may follow the instructions at https://namemc.com/claim-your-profile, then link your "
                "Discord account to your NameMC profile. After doing this, please ping a staff member in the "
                "verification channel with a link to your NameMC account.",
                "inline": False
            },
            5: {
                "name": "I don't want people to know what my Minecraft account is. What do I do?",
                "value": "You can toggle your profile visibility via the +toggleprofile command. Note that staff "
                "members will still be able to access this information.",
                "inline": False
            },
        }
    },

    "verify reason": {
        "embedTitle": "The Purpose of Verification",
        "embedDescription": "It's clear that some users don't understand why verification is necessary. We have this "
        "system for a myriad of reasons, including but not limited to:\n\n-Knowing who you are\n-Alt prevention\n"
        "-Raid prevention\n-Incorporating more game-tailored features into the bot\n-Moderation",
        "embedColor": discord.Color.blue(),
        "fields": {},
        }
}
