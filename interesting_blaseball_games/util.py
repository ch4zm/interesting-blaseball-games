import json
import os
import blaseball_core_game_data as gd


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

SHORT2LONG_JSON = os.path.join(data_path, "short2long.json")

DALE_SAFE = "Dale"
DALE_UTF8 = "Dal\u00e9"

FULL_DALE_SAFE = "Miami Dale"
FULL_DALE_UTF8 = "Miami Dal\u00e9"


def get_league_division_team_data():
    """
    Get a list of all leagues, all divisions, and all teams
    for creating command line flag options - includes old leagues
    and divisions.
    """
    tds = json.loads(gd.get_teams_data())

    leagues = set()
    divisions = set()
    teams = set()
    for i in range(len(tds)):
        td = tds[i]
        leagues_ = sorted(list(td['leagues'].keys()))
        divisions_ = sorted(list(td['divisions'].keys()))
        leagues = leagues.union(leagues_)
        divisions = divisions.union(leagues_)

        teams_ = []
        for league_ in leagues_:
            teams_ += td['leagues'][league_]
        teams = teams.union(teams_)

    leagues = sorted(list(leagues))
    teams = sorted(list(teams))
    divisions = sorted(list(divisions))

    return (leagues, divisions, teams)


def league_to_teams(league):
    """For a given league, return a list of all teams in that league."""
    tds = json.loads(gd.get_teams_data())
    teams = []
    if season is None:
        for i in range(len(tds)):
            td = tds[i]
            leagues = sorted(list(td['leagues'].keys()))
            if league in leagues:
                teams = sorted(list(td['leagues'][league]))
                break
    else:
        td = tds[season]
        leagues = sorted(list(td['leagues'].keys()))
        if league in leagues:
            teams = sorted(list(td['leagues'][league]))

    if len(teams)==0:
        raise Exception("Error: Could not find any teams in league %s"%(league))
    return teams


def division_to_teams(division):
    """For a given division, return a list of all teams in that league."""
    tds = json.loads(gd.get_teams_data())
    teams = []
    if season is None:
        for i in range(len(tds)):
            td = tds[i]
            divisions = sorted(list(td['divisions'].keys()))
            if division in divisions:
                teams = sorted(list(td['divisions'][division]))
                break
    else:
        td = tds[season]
        divisions = sorted(list(td['divisions'].keys()))
        if division in divisions:
            teams = sorted(list(td['divisions'][division]))

    if len(teams)==0:
        raise Exception("Error: Could not find any teams in division %s"%(division))
    return teams


def get_short2long():
    """Get the map of team nicknames to team full names"""
    short2long = None
    if os.path.exists(SHORT2LONG_JSON):
        with open(SHORT2LONG_JSON, 'r') as f:
            short2long = json.load(f)
    else:
        raise FileNotFoundError("Missing team nickname to full name data file: %s"%(SHORT2LONG_JSON))
    return short2long


def sanitize_dale(s):
    """Utility function to make CLI flag value easier to set"""
    if s == DALE_UTF8:
        return DALE_SAFE
    elif s== FULL_DALE_UTF8:
        return FULL_DALE_SAFE
    else:
        return s

