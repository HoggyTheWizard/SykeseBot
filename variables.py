import config

verified_role_id = 893933214656233563
unverified_role_id = 893933243768918016
mod_id = 891123241765179472

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

group_tiers = {
    889717866239234088: 0,  # friend (everyone)
    890700948710772766: 1,  # super friend
    892475435290607646: 1,  # blue booster
    911038229862563911: 1,  # birthday
    891123241765179472: 4,  # chat moderator
    889717645300072529: 5,  # admin (currently sykese's custom role)
}
