def cog_name_formatted():
    try:
        cog_dict = {
            "general": "General",
            "help_command": "Help",
            "verify_commands": "Verification"
        }
        return cog_dict
    except:
        return None