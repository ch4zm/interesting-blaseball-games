import sys
import os
import json
import configargparse
from .view import NAMESTYLE_CHOICES, RichView, MarkdownView
from .game_data import REASON2FUNCTION
from .util import (
    root_path, 
    data_path,
    get_league_division_team_data,
    league_to_teams,
    division_to_teams
)


"""
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


def main(sysargs = sys.argv[1:]):

    p = configargparse.ArgParser()

    # These are safe for command line usage
    LEAGUES, DIVISIONS, ALLTEAMS = get_league_division_team_data()

    p.add('-v',
          '--version',
          required=False,
          default=False,
          action='store_true',
          help='Print program name and version number and exit')

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

    # Output format
    p.add('--rich',
          action='store_true',
          default=True,
          help='Print data using rich to format tables (default)')
    p.add('--markdown',
          action='store_true',
          default=False,
          help='Print data in Markdown table format')
    p.add('--output',
          required=False,
          type=str,
          default='',
          help='Specify the name of the Markdown output file, for use with --markdown flags')

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

    # Print help, if no arguments provided
    if len(sysargs)==0:
        p.print_help()
        exit(0)

    # Parse arguments
    options = p.parse_args(sysargs)

    # If the user asked for the version,
    # print the version number and exit.
    if options.version:
        from . import _program, __version__
        print(_program, __version__)
        sys.exit(0)

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
    else:
        try:
            _ = [int(j) for j in options.season]
        except ValueError:
            raise Exception("Error: you must provide integers to the --season flag: --season 1 --season 2")

    if options.markdown:
        v = MarkdownView(options)
        v.make_table()
    else:
        v = RichView(options)
        v.make_table()


if __name__ == '__main__':
    main()
