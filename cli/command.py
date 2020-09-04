import sys
import os
import json
import configargparse
from .view import NAMESTYLE_CHOICES, View
from .game_data import REASON2FUNCTION
from . import _program


logo = r"""

 ____  _  _  ____                                                 
(_  _)/ )( \(  __)                                                
  )(  ) __ ( ) _)                                                 
 (__) \_)(_/(____)                                                
  ___  __   _  _  _  _  __  ____  ____  __  __   __ _  ____  ____ 
 / __)/  \ ( \/ )( \/ )(  )/ ___)/ ___)(  )/  \ (  ( \(  __)(  _ \
( (__(  O )/ \/ \/ \/ \ )( \___ \\___ \ )((  O )/    / ) _)  )   /
 \___)\__/ \_)(_/\_)(_/(__)(____/(____/(__)\__/ \_)__)(____)(__\_)
  __  ____    ____   __  __  __ _   ___                           
 (  )/ ___)  (    \ /  \(  )(  ( \ / __)                          
  )( \___ \   ) D ((  O ))( /    /( (_ \                          
 (__)(____/  (____/ \__/(__)\_)__) \___/                          
  __      ___  ____  ____   __  ____      __   __  ____           
 / _\    / __)(  _ \(  __) / _\(_  _)   _(  ) /  \(  _ \          
/    \  ( (_ \ )   / ) _) /    \ )(    / \) \(  O )) _ (          
\_/\_/   \___/(__\_)(____)\_/\_/(__)   \____/ \__/(____/ 


"""


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

GAMES_DATA_JSON = os.path.join(data_path, "games_data_trim.json")
TEAMS_DATA_JSON = os.path.join(data_path, "teams_data.json")

DALE_SAFE = "Dale" # for command line
DALE_UTF8 = "Dal\u00e9" # for display


def main(sysargs = sys.argv[1:]):

    p = configargparse.ArgParser()

    # These are safe for command line usage (no accent in Dale)
    LEAGUES, DIVISIONS, ALLTEAMS = get_league_division_team_data()

    p.add('-c',
          '--config',
          required=False,
          is_config_file=True,
          help='config file path')

    # -----
    # View options with short flags
    p.add('-a',
          '--name-style',
          required=False,
          choices=NAMESTYLE_CHOICES,
          default='short',
          help='specify style for team names (long/short/emoji)')

    p.add('-n',
          '--n-results',
          required=False,
          type=int,
          default=10,
          help='max number of rows to show in each table (default 10)')

    # -----
    # View options
    p.add('--reason',
          required=False,
          choices=list(REASON2FUNCTION.keys()),
          default='all',
          help='the reason that a game is interesting (controls which tables are shown, defaults to all)')

    p.add('--season',
          required=False,
          action='append',
          choices=['1', '2', '3', '4', '5'],
          help='specify season (use flag multiple times for multiple seasons, no --seasons flag means all data)')

    p.add('--postseason',
          required=False,
          default=False,
          action='store_true',
          help='limit games to postseason games only')

    # View options for pitcher
    p.add('--winning-pitcher',
          required=False,
          default=False,
          action='store_true',
          help='include winning pitcher in columns displayed')

    p.add('--losing-pitcher',
          required=False,
          default=False,
          action='store_true',
          help='include losing pitcher in columns displayed')

    # View options for columns
    g = p.add_mutually_exclusive_group()
    g.add('--win-loss',
          action='store_true',
          default=True,
          help='display teams by winner (left column)/loser (right column)')
    g.add('--home-away',
          action='store_true',
          default=False,
          help='display teams by home (left column)/away (right column)')

    # -----
    # Data filtering options
    h = p.add_mutually_exclusive_group()
    h.add('--team',
          choices=ALLTEAMS,
          action='append',
          help='specify team (use flag multiple times for multiple teams)')
    h.add('--division',
          choices=DIVISIONS,
          action='append',
          help='specify division (use flag multiple times for multiple divisions)')
    h.add('--league',
          choices=LEAGUES,
          action='append',
          help='specify league')

    # -----

    # Parse arguments
    options = p.parse_args(sys.argv[1:])

    # -----
    # If the user specified a division or a league,
    # turn that into a list of teams for them
    if options.division:
        divteams = []
        for div in options.division:
            divteams += division_to_teams(div)
        options.team = divteams
        options.division = None
    if options.league:
        leateams = []
        for lea in options.league:
            leateams += league_to_teams(lea)
        options.team = leateams
        options.league = None

    # If nothing was supplied for team/division/league, use all teams
    if not options.team and not options.division and not options.league:
        options.team = ALLTEAMS

    # If nothing was provided for seasons, set it to 'all'
    if not options.season:
        options.season = ['all']

    # No more user input required, so convert Dale back to utf8
    options.team = [DALE_UTF8 if x==DALE_SAFE else x for x in options.team]

    v = View(options)
    v.make_table()


def get_league_division_team_data():
    """
    Get a list of leagues, divisions, and teams.
    This is for use in creating CLI flag values,
    so we replace Dal\u00e9 with Dale.
    """
    with open(TEAMS_DATA_JSON, 'r') as f:
        td = json.load(f)
    leagues = sorted(list(td['leagues'].keys()))
    divisions = sorted(list(td['divisions'].keys()))
    teams = []
    for league in leagues:
        teams += td['leagues'][league]
    teams = sorted(list(teams))
    teams = [_sanitize_dale(s) for s in teams]
    return (leagues, divisions, teams)


def league_to_teams(league):
    """
    For a given league, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    with open(TEAMS_DATA_JSON, 'r') as f:
        td = json.load(f)
    teams = []
    teams += td['leagues'][league]
    teams = [_sanitize_dale(s) for s in teams]
    return teams


def division_to_teams(division):
    """
    For a given division, return a list of all teams in that league.
    We replace Dal\u00e9 with Dale (see above).
    """
    with open(TEAMS_DATA_JSON, 'r') as f:
        td = json.load(f)
    teams = []
    teams += td['divisions'][division]
    teams = [_sanitize_dale(s) for s in teams]
    return teams


def _sanitize_dale(s):
    """Utility function to make CLI flag value easier to set"""
    if s == DALE_UTF8:
        return DALE_SAFE
    else:
        return s


if __name__ == '__main__':
    main()
