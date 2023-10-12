from collections import Counter

from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)


tournaments_fields = {
    "Name",
    "Region",
    "League",
    "TournamentLevel",
    "OverviewPage",
}

region = "International"
year = 2023
# date_start = "2022-09-29"
name = "World Championship"
where = " AND ".join(
        [
            # One constraint per variable
            f"t.{field_name}='{value}'"
            for field_name, value in [
                ("Region", region),
                ("Year", year),
				# ("DateStart", date_start),
				("League", name)
            ]
            # We don’t filter on variables that are None
            if value is not None
        ]
)

# TODO: Don't include WQS
where += " AND t.Name != 'Worlds Qualifying Series 2023'"

# response = site.cargo_client.query(
# 	tables="Tournaments, Leagues",
# 	join_on="Tournaments.League = Leagues.League",
# 	fields=f"Leagues.League_Short, {', '.join(f'Tournaments.{field}' for field in tournaments_fields)}",
# 	where=where
# )
sg_fields = {
	"Team1",
	"Team2",
	"Team1Bans",
	"Team2Bans",
	"Team1Picks",
	"Team2Picks"
}
response = site.cargo_client.query(
	tables="Tournaments=t, ScoreboardGames=sg", # ScoreboardPlayers=sp",
	join_on="t.OverviewPage = sg.OverviewPage", # t.OverviewPage=sp.OverviewPage",
	fields=f"{', '.join(f't.{field}' for field in tournaments_fields)}, {', '.join(f'sg.{field}' for field in sg_fields)}", # , sp.Name, sp.Champion, sp.Deaths",
	where=where,
	limit=100
)
print(response)
# Use Tournaments to find Games in 2022
# (Don't need?) Link Tournaments to Leagues to find "World Championship"
# link Tournaments to ScoreboardGames to find match data (join_on OverviewPage)
all_banned = Counter()
all_picked = Counter()
for item in response:
	for key, value in item.items():
		print(key,value)
		if "Bans" in key and value:
			all_banned.update(value.split(','))

for item in response:
	for key, value in item.items():
		if "Picks" in key and value:
			all_picked.update(value.split(','))

print("Banned:")
for key, value in all_banned.most_common():
	print(key,value)

print("")
print("Most Picked:")
for key, value in all_picked.most_common():
	print(key,value)
print(len(response))
