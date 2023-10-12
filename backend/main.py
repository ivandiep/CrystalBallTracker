from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import queries

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/champions/most-picked", tags=["Champions"])
def get_most_picked():
    most_picked = queries.most_picked()
    return {k:v for k,v in most_picked}


@app.get("/champions/most-banned", tags=["Champions"])
def get_most_banned():
    most_banned = queries.most_banned()
    return {k:v for k,v in most_banned}

@app.get("/champions/highest-winrate", tags=["Champions"])
def get_highest_winrate():
    highest_winrate = queries.highest_winrate()
    return highest_winrate

@app.get("/champions/most-flexed", tags=["Champions"])
def get_most_flexed():
    most_flexed = queries.most_flexed()
    return most_flexed

@app.get("/champions/most-deaths", tags=["Champions"])
def get_most_deaths():
    most_deaths = queries.most_deaths()
    return {k:v for k,v in most_deaths}

@app.get("/players/highest-kda", tags=["Players"])
def get_highest_kda():
    return queries.highest_kda()

@app.get("/players/most-unique-champs", tags=["Players"])
def get_most_unique_champs():
    return queries.most_unique_champs()

@app.get("/players/one-pentakill", tags=["Players"])
def get_one_penta():
    return queries.one_penta()

@app.get("/players/most-first-bloods", tags=["Players"])
def get_most_first_bloods():
    return {k:v for k,v in queries.most_first_bloods()}

@app.get("/players/most-kills", tags=["Players"])
def get_most_kills():
    return queries.most_kills()

@app.get("/teams/most-unique-champs", tags=["Teams"])
def get_team_most_unique_champs():
    return queries.team_most_unique_champs()

@app.get("/events/total-pentakills", tags=["Events"])
def get_total_pentas():
    return queries.total_pentas()

@app.get("/events/longest-game", tags=["Events"])
def get_longest_game():
    return queries.longest_game()

@app.get("/events/most-dragons", tags=["Events"])
def get_most_dragons():
    return {k:v for k,v in queries.most_dragons()}