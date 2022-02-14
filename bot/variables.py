import config

verified_role_id = 893933214656233563
unverified_role_id = 893933243768918016
mod_id = 891123241765179472

owner_ids = [524755715655467019, 192097613087113220]

main_guilds = [
        889697074491293736,  # Sykese
        707963219536248982  # test server
        ]
test_guilds = guilds = [
        707963219536248982  # test server
        ]

if config.host == "master":
    guilds = main_guilds
else:
    guilds = test_guilds

mod_id = 891123241765179472
developer_id = 892811975329980447

moderator_ids = [mod_id, developer_id]
manager_ids = [developer_id]
