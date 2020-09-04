# `fetch_games_data.py`

**Thanks to Github user [@dlareau](https://github.com/dlareau) for
coming up with the original version of this script. See
[this gist](https://gist.github.com/dlareau/c28c54937a16fdd7edac5bda9b8e936d)
for the original implementation.**

This script will call the blaseball.com/games API endpoint.
That API returns the last event of the game in JSON format.
The script then trims that data (there is a lot of extraneous
information in it), drops games from the great void of Season 4
(games 80-86), and adds a few derived quantities.

The columns in the data frame are as follows:

* id
* season
* day
* awayOdds
* awayPitcherName
* awayScore
* awayTeamEmoji
* awayTeamName
* awayTeamNickname
* homeOdds
* homePitcherName
* homeScore
* homeTeamEmoji
* homeTeamName
* homeTeamNickname
* isPostseason
* losingTeamName
* losingTeamNickname
* losingTeamEmoji
* losingScore
* losingOdds
* losingPitcherName
* runDiff
* shame
* whoWon
* winningTeamName
* winningTeamNickname
* winningTeamEmoji
* winningScore
* winningOdds
* winningPitcherName

