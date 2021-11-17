# interesting-blaseball-games

`interesting-blaseball-games` is a command-line tool for finding interesting blaseball games.

**Interesting blaseball games** are defined as:

* games with large run differentials
* games where loser was shut out (scored zero runs)
* games where loser was shamed
* games won by the underdog

The user specifies different criteria (such as season, team, or
type of interesting blaseball game) and the program prints out
a series of tables containing game summaries.

## Table of Contents

* [Screenshots](#screenshots)
* [Installation](#installation)
    * [pip](#pip)
    * [source](#source)
* [Quick Start](#quick-start)
    * [Command line flags](#command-line-flags)
    * [Configuration file](#configuration-file)
* [Output formats](#output-formats)
* [Configuration Examples](#configuration-examples)
* [Data](#data)
* [Software architecture](#software-architecture)
* [Who is this tool for?](#who-is-this-tool-for)
* [Future work](#future-work)
* [Libraries Used](#libraries-used)

## Screenshots

The `interesting-blaseball-games` command line tool allows you to pick
teams, leagues, or divisions, as well as seasons, and you can also filter
on postseason games:

![Postseason shame](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s1a.png)

You can also include the winning or losing pitcher, or both:

![Shutouts with winning pitcher](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s1b.png)

![Blowouts with losing pitcher](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s1c.png)

The program gives you the ability to display team names in different formats:
the full name, the nickname, or the emoji:

![All interesting emoji names](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s2a.png)

The command line flags support arguments with spaces, too:

![Shoe Thieves interesting emoji names](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s2b.png)

An example of the full (long) name format:

![Long name format](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s3a.png)

Finally, information is organized in an intuitive and readable way:

![Readable table with winning and losing pitcher info](https://github.com/ch4zm/interesting-blaseball-games/raw/master/img/s3b.png)

## Installation

### pip

```
pip install git+https://github.com/ch4zm/blaseball-core-game-data.git#egg=blaseball_core_game_data
pip install git+https://github.com/ch4zm/interesting-blaseball-games.git#egg=interesting_blaseball_games
```

### source

If installing from source, it is recommended you install the package
into a virtual environment. For example:

```
virtualenv vp
source vp/bin/activate
```

To install the package, run

```
python setup.py build install
```

Now test that the tool is available on the command line, and try out
a command to print some interesting games from season 3:

```
which interesting-blaseball-games
interesting-blaseball-games --season 3 --team Sunbeams
```


## Quick Start

The way `interesting-blaseball-games` works is, it creates a data frame
object, applies some filters to it based on command line flags provided
by the user, then runs the data frame through a data viewer (which makes
the nice tables). All command line flags can also be specified in a config
file.

### Command line flags

Command line flags are grouped into data options and view options.

Data options:

* **Season**: set season for game data using `--season`. For multiple seasons, repeat the flag: `--season 1 --season 2`
* **Postseason**: `--postseason` flag limits data shown to postseason games only
* Specify only one of the following:
    * **Team**: use the `--team` flag to specify the short name of your team (use `--help` to see
      valid choices). For multiple teams, use multiple `--team` flags.
    * **Division**: use the `--division` flag to specify the name of a division. Surround division
      name in quotes, e.g., `--division "Lawful Evil"`
    * **League**: use the `--league` flag to specify the Good/Evil league

View options:

* **Reason**: use the `--reason` specify a reason why a game is interesting (blowout, shutout, shame, underdog); defaults to all.
* **Win-Loss** or **Home-Away**: `--win-loss` and `--home-away` lays out the table data as winner (left)/loser (right), or as home (left)/away (right)
* **Winning Pitcher** and **Losing Pitcher**: `--winning-pitcher` and `--losing-pitcher` flags will include the name of the winning/losing pitcher in the table
* **Output Format**: Specify an output format for the tables:
    * **Rich**: add the `--rich` flag to print the tables formatted for the console using rich, a Python formatting library (this is the default behavior)
    * **HTML**: add the `--html` flag to output the tables as HTML tables
    * **Markdown**: add the `--markdown` flag to output the tables as Markdown tables
* **Output file**: (optional) use the `--output` flag to specify an output file when using `--html` or `--markdown` (if left out, HTML and Markdown are printed to the console)

Using a configuration file:

* **Config file**: use the `-c` or `--config` file to point to a configuration file (see next section).


### Configuration file

(Note: several configuration file examples are provided in a section below.)

Every command line flag can be specified in a configuration file as well.
To reproduce the following command line call,

```
interesting-blaseball-games --season 1 --season 2 --team Sunbeams --team Tigers --postseason --winning-pitcher
```

we could create a configuration file named `config.ini` with the contents:

```
season = [1, 2]
team = Sunbeams
team = Tigers
postseason
winning-pitcher
```

and run `interesting-blaseball-games` specifying that configuration file:

```
interesting-blaseball-games --config config.ini
# or
interesting-blaseball-games -c config.ini
```

This would produce identical output to the command with all the flags.

You can also use both a config file and command line flags; the command line flags will take
precedence over config file options if a parameter is specified by both.


## Output Formats

This command line utility enables output in three formats: tables formatted for the command line,
html (to stdout or to a file), or markdown tables (to stdout or to a file).

By default, the tool will print tables formatted for the command line.

If the `--html` flag is added, the tool will dump out the tables in HTML format using the
pandas DataFrame function `to_html()` under the hood. If the `--output` flag specifies
a filename, the HTML for all the tables is in that file.

If the `--markdown` flag is added, the tool will dump out tables in a format suitable for
Markdown documents. If the `--output` flag specifies a filename, the Markdown for the tables
will be in that file.


## Configuration Examples

See [`config.example.ini`](https://github.com/ch4zm/interesting-blaseball-games/tree/master/config.example.ini)
in the repo for an example config file.

Only show interesting games from seasons 1 and 2 involving the Sunbeams and the Tacos:

```
[data]
season = [1, 2]
team = [Tacos, Sunbeams]
```

Limit this to shutout games only:

```
[data]
season = [1, 2]
team = [Tacos, Sunbeams]

[view]
reason = shutout
```

Only show interesting games from the season 3 postseason:

```
[data]
season = 3
postseason = true
```

Show team names as emojis:

```
[data]
season = 3
postseason = true

[view]
name-style = emoji
```

Organize the results by winner/loser instead of home/away:

```
[data]
season = 3
postseason = true

[view]
name-style = emoji
win-loss = true
```

Show the 15 biggest blowout games in blaseball history, along with the name of the
losing pitcher who blew it:

```
[view]
reason = blowout
n-results = 15
win-loss = true
losing-pitcher = true
```

Repeat the above command, but output the results as HTML to the file `alltime_blowouts.html`:

```
[view]
reason = blowout
n-results = 15
win-loss = true
losing-pitcher = true
html
output = alltime_blowouts.html
```

Repeat the above command, but output the results as Markdown to the file `alltime_blowouts.md`:

```
[view]
reason = blowout
n-results = 15
win-loss = true
losing-pitcher = true
markdown
output = alltime_blowouts.md
```

## Data

The data set used by this tool comes from `blaseball.com`'s `/games` API endpoint.
The data set is imported from [`blaseball-core-game-data`](https://github.com/ch4zm/blaseball-core-game-data).


## Software architecture

This software consists of three parts:

* The command line flag and config file parser (uses `configargparse` library)
* The GameData object that stores the game data in a Pandas data frame (uses `pandas` library)
* The View object that provides a presentation layer on top of the Pandas data frame (uses `rich` library)


## Who is this tool for?

This tool is for the blaseball community. It will be useful to people
interested in exploring game data, people who are brainstorming about
lore for their team, and people who are looking for a starting point
for developing their own blaseball tool.


## Future work

* Add close games (1 run - sorted by score, low to hi or hi to low?)
    * maxedout - high-scoring, one-run games
    * defensive - low-scoring, one-run games

## Libraries Used

This command line tool uses the following libraries under the hood:

* [blaseball-core-game-data](https://github.com/ch4zm/blaseball-core-game-data)
* [rich](https://github.com/willmcgugan/rich) for formatting text and tables
* [pandas](https://pandas.pydata.org/) for organizing/filtering data
* [configarparse](https://github.com/bw2/ConfigArgParse) for handling CLI arguments
