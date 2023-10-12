from collections import Counter
import json

from mwrogue.esports_client import EsportsClient
from mwrogue.auth_credentials import AuthCredentials

credentials = AuthCredentials(user_file="me")
site = EsportsClient('lol', credentials=credentials)

tournaments_fields = {
    "Name",
    "Region",
    "OverviewPage",
}

region = "International"
year = 2023
league = "World Championship"
where = " AND ".join(
        [
            # One constraint per variable
            f"t.{field_name}='{value}'"
            for field_name, value in [
                ("Region", region),
                ("Year", year),
				("League", league)
            ] 
            # We don’t filter on variables that are None
            if value is not None
        ]
) + " AND t.Name != 'Worlds Qualifying Series 2023'" # Don't include WQS 2023


pick_fields = {
	"Team1Picks",
	"Team2Picks"
}
ban_fields = {
	"Team1Bans",
	"Team2Bans",
}
winrate_fields = {
	"Champion",
	"PlayerWin"
}
flex_fields = {
	"Champion",
	"Role_Number"
}
death_fields = {
	"Champion",
	"Deaths"
}

# Champions
### Most Picked
def most_picked():
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardGames=sg",
		join_on="t.OverviewPage = sg.OverviewPage",
		fields=f"{', '.join(f't.{field}' for field in tournaments_fields)}, {', '.join(f'sg.{field}' for field in pick_fields)}",
		where=where,
	)
	# print(response)
	all_picked = Counter()
	for item in response:
		for key, value in item.items():
			if "Picks" in key and value:
				all_picked.update(value.split(','))

	return all_picked.most_common()

### Most Banned
def most_banned():
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardGames=sg",
		join_on="t.OverviewPage = sg.OverviewPage",
		fields=f"{', '.join(f't.{field}' for field in tournaments_fields)}, {', '.join(f'sg.{field}' for field in ban_fields)}",
		where=where,
	)

	all_banned = Counter()
	for item in response:
		for key, value in item.items():
			if "Bans" in key and value:
				all_banned.update(value.split(','))

	return all_banned.most_common()

### Highest Winrate
def highest_winrate():
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=f"{', '.join(f't.{field}' for field in tournaments_fields)}, {', '.join(f'sp.{field}' for field in winrate_fields)}",
		where=where,
	)

	win = Counter()
	total = Counter()
	for item in response:
		item.move_to_end('PlayerWin')
		curr_champ = ""
		for key, value in item.items():
			if "Champion" in key and value:
				curr_champ = value
				total.update([value])
			if "PlayerWin" in key and value and "Yes" in value:
				win.update([curr_champ])

	cleaned_total = Counter({k:c for k, c in total.items() if c >= 5})
	zipped_winrate = {k1:(v1/v2) for k1,v1 in win.items() for k2,v2 in cleaned_total.items() if k1==k2}
	sorted_winrate = dict(sorted(zipped_winrate.items(), key=lambda item: item[1], reverse=True))

	for key, value in sorted_winrate.items():
		sorted_winrate[key] = "{value:.2f}%".format(value=value*100)
	return sorted_winrate

### Most Flexed
def most_flexed():
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=f"{', '.join(f't.{field}' for field in tournaments_fields)}, {', '.join(f'sp.{field}' for field in flex_fields)}",
		where=where,
	)
	all_flexed = {}
	for item in response:
		item.move_to_end('Role Number')
		curr_champ = ""
		for key, value in item.items():
			if "Champion" in key and value:
				curr_champ = value
				if value not in all_flexed:
					all_flexed[value] = set()
			if "Role Number" in key and value:
				all_flexed[curr_champ].add(value)

	sorted_flexed = dict(sorted(all_flexed.items(), key=lambda item: len(item[1]), reverse=True))
	for key, value in sorted_flexed.items():
		sorted_flexed[key] = len(value)
	return sorted_flexed

### Most Deaths
def most_deaths():
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=f"{', '.join(f't.{field}' for field in tournaments_fields)}, {', '.join(f'sp.{field}' for field in death_fields)}",
		where=where,
	)
	all_deaths = {}

	for item in response:
		item.move_to_end('Deaths')
		curr_champ = ""
		for key, value in item.items():
			if "Champion" in key and value:
				curr_champ = value
				if value not in all_deaths:
					all_deaths[value] = 0
			if "Deaths" in key and value:
				all_deaths[curr_champ] += int(value)
	all_deaths = Counter(all_deaths)
	return all_deaths.most_common()

# Players
### Highest KDA
def highest_kda():
	sp_fields = {
		"Name",
		"Kills",
		"Deaths",
		"Assists"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=f"{', '.join(f'sp.{field}' for field in sp_fields)}",
		where=where,
	)
	
	all_players = {}
	for item in response:
		if item["Name"]:
			if item["Name"] not in all_players:
				all_players[item["Name"]] = {
					"K": 0,
					"D": 0,
					"A": 0,
				}
			all_players[item["Name"]]["K"] += int(item["Kills"])
			all_players[item["Name"]]["D"] += int(item["Deaths"])
			all_players[item["Name"]]["A"] += int(item["Assists"])
	all_players_kda = {k:round((v["K"]+v["A"])/v["D"], 2) if v["D"] != 0 else -1 for k,v in all_players.items()}
	sorted_all_players_kda = {k: v for k, v in sorted(all_players_kda.items(), key=lambda item: item[1], reverse= True)}

	# 369 case (TODO: find root cause)
	sorted_all_players_kda = {"_369" if k == "369" else k:v for k,v in sorted_all_players_kda.items()}
	return sorted_all_players_kda

### Most Unique Champs
def most_unique_champs():
	sp_fields = {
		"Name",
		"Champion"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=f"{', '.join(f'sp.{field}' for field in sp_fields)}",
		where=where,
	)

	all_players = {}
	for item in response:
		if item["Name"] not in all_players:
			all_players[item["Name"]] = set()
		all_players[item["Name"]].add(item["Champion"])

	unique_champ_count = {k:len(v) for k,v in all_players.items()}
	sorted_unique_champ_count = {k: v for k, v in sorted(unique_champ_count.items(), key=lambda item: item[1], reverse= True)}
	# 369 case (TODO: find root cause)
	sorted_unique_champ_count = {"_369" if k == "369" else k:v for k,v in sorted_unique_champ_count.items()}
	return sorted_unique_champ_count

### At least One Penta
def one_penta():
	p_fields = {
		"Name"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, Pentakills=p",
		join_on="t.OverviewPage = p.OverviewPage",
		fields=', '.join(f'p.{field}' for field in p_fields),
		where=where,
	)
	one_penta = set()
	for item in response:
		if item["Name"]: # removes None items
			one_penta.add(item["Name"])
	return {"Pentakills": one_penta}

### Most First Bloods
def most_first_bloods():
	p_fields = {
		"RiotPlatformGameId"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, PostgameJsonMetadata=p",
		join_on="t.OverviewPage = p.OverviewPage",
		fields=', '.join(f'p.{field}' for field in p_fields),
		where=where,
	)

	all_first_bloods = Counter()
	for item in response:
		if item["RiotPlatformGameId"]:
			data, timeline = site.get_data_and_timeline(item["RiotPlatformGameId"], 5)
			for player in data["participants"]:
				if player["firstBloodKill"]:
					all_first_bloods.update([player["summonerName"]])
					continue

	return all_first_bloods.most_common()

### Most Kills in One Game
def most_kills():
	sp_fields = {
		"Name",
		"Kills"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=', '.join(f'sp.{field}' for field in sp_fields),
		where=where,
	)

	all_players = {}
	for item in response:
		if item["Name"]:
			if item["Name"] not in all_players:
				all_players[item["Name"]] = 0
			all_players[item["Name"]] = max(all_players[item["Name"]], int(item["Kills"]))
	sorted_all_players = dict(sorted(all_players.items(), key= lambda item:item[1], reverse=True))

	# 369 case (TODO: find root cause)
	sorted_all_players = {"_369" if k == "369" else k:v for k,v in sorted_all_players.items()}
	return sorted_all_players

# Teams
### Win Worlds (skip)
### Place 1st in Play-in Group A
#### Manual? FNC
### Place 1st in Play-in Group B
#### Manual? DRX
### Team with most unique champs
def team_most_unique_champs():
	sp_fields = {
		"Team",
		"Champion"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardPlayers=sp",
		join_on="t.OverviewPage = sp.OverviewPage",
		fields=f"{', '.join(f'sp.{field}' for field in sp_fields)}",
		where=where,
	)

	all_teams = {}
	for item in response:
		if item["Team"] not in all_teams:
			all_teams[item["Team"]] = set()
		all_teams[item["Team"]].add(item["Champion"])

	unique_champ_count = {k:len(v) for k,v in all_teams.items()}
	sorted_unique_champ_count = {k: v for k, v in sorted(unique_champ_count.items(), key=lambda item: item[1], reverse= True)}
	
	return sorted_unique_champ_count

# Event
### Reverse Sweeps
##### 0
### Total Pentas
def total_pentas():
	p_fields = {
		"Name"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, Pentakills=p",
		join_on="t.OverviewPage = p.OverviewPage",
		fields=', '.join(f'p.{field}' for field in p_fields),
		where=where,
	)
	total_pentas = 0
	for item in response:
		if item["Name"]: # removes None items
			total_pentas += 1
	return {"Total Pentakills": total_pentas}
### Longest Game
def longest_game():
	sg_fields = {
		"Gamelength",
		"Gamelength_Number"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, ScoreboardGames=sg",
		join_on="t.OverviewPage = sg.OverviewPage",
		fields=', '.join(f'sg.{field}' for field in sg_fields),
		where=where,
	)
	longest_game_num = 0
	longest_game_timer= "00:00"
	for item in response:
		if item["Gamelength Number"] and float(item["Gamelength Number"]) > longest_game_num:
			longest_game_num = float(item["Gamelength Number"])
			longest_game_timer = item["Gamelength"]

	return {"Longest Gametime": longest_game_timer}
### Baron Steals
##### Manual Input 6
### Which Dragon
def most_dragons():
	p_fields = {
		"RiotPlatformGameId"
	}
	response = site.cargo_client.query(
		tables="Tournaments=t, PostgameJsonMetadata=p",
		join_on="t.OverviewPage = p.OverviewPage",
		fields=', '.join(f'p.{field}' for field in p_fields),
		where=where,
	)

	drag_count = Counter()
	baron_steal_count = 0
	for item in response:
		if item["RiotPlatformGameId"]:
			data, timeline = site.get_data_and_timeline(item["RiotPlatformGameId"], 5)

			for frame in timeline["frames"]:
				for event in frame["events"]:
					if "monsterSubType" in event:
						drag_count.update([event["monsterSubType"]])
						continue

	return drag_count.most_common()


# Use Tournaments to find Games in 2022
# (Don't need?) Link Tournaments to Leagues to find "World Championship"
# link Tournaments to ScoreboardGames to find match data (join_on OverviewPage)

# print(len(response))

