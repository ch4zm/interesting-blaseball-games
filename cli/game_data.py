import os
import pandas as pd


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
data_path = os.path.abspath(os.path.join(root_path, 'data'))

GAMES_DATA_JSON = os.path.join(data_path, "games_data_trim.json")


def blowout(df):
    """
    Filter the dataframe of game data on blowouts
    (games with the largest run differential).
    Returns: tuple (string description, dataframe tabledata)
    """
    desc = "Blowout games (games with high scores and high run differentials)"
    filt = df.sort_values(['winningScore', 'runDiff'], ascending=[False, False])
    return (desc, filt)


def shutout(df):
    """
    Filter the dataframe of game data on shutouts
    (games where one team has zero runs).
    Returns: tuple (string description, pd dataframe)
    """
    desc = "Shutout games (games where the loser had zero runs)"
    filt = df.loc[df['losingScore']==0]
    filt = filt.sort_values('runDiff', ascending=False)
    return (desc, filt)


def shame(df):
    """
    Filter the dataframe of game data on shame
    (games where one team was shamed).

    Returns: tuple (string description, pd dataframe)
    """
    desc = "Shame games (games where the loser was shamed)"
    filt = df.loc[df['shame']==True]
    filt = filt.sort_values('runDiff', ascending=False)
    return (desc, filt)


def underdog(df):
    """
    Filter the dataframe of game data on underdog wins
    (games where the team with lower odds won).
    Returns: tuple (string description, pd dataframe)
    """
    desc = "Underdog games (games where the underdog won with large run differential)"
    filt = df.loc[df['winningOdds']<0.5]
    filt = filt.sort_values('runDiff', ascending=False)
    return (desc, filt)


# Map reason strings to their corresponding filter function
REASON2FUNCTION = {
    "blowout": [blowout],
    "shutout": [shutout],
    "shame": [shame],
    "underdog": [underdog],
    "all": [blowout, shutout, shame, underdog],
}


class GameData(object):
    """
    Class representing a data frame with game data.
    Data is filtered immediately on load, based on the data
    filters the user has specified in the config.
    """
    def __init__(self, options):
        """Load the data set into self.df"""
        if os.path.exists(GAMES_DATA_JSON):
            self.df = pd.read_json(GAMES_DATA_JSON)
        else:
            raise FileNotFoundError("Missing game data file: %s"%(GAMES_DATA_JSON))

        # Drop tie games
        self.df = self._filter_ties()

        # Fiter data based on user configuration
        self.df = self._season_filter_df(options.season)
        self.df = self._postseason_filter_df(options.postseason)
        self.df = self._team_filter_df(options.team)
        self.reason = options.reason

    def _filter_ties(self):
        mask = self.df.loc[self.df['homeScore']!=self.df['awayScore']]
        return mask

    def _season_filter_df(self, seasons):
        """
        Filter game data on season number(s). The dataframe's season numbers
        (from the blaseball API) are zero-indexed.
        """
        if 'all' in seasons:
            # Get all unique 0-indexed season values
            seasons = list(set(self.df['season'].values))
        else:
            # User provides 1-indexed season values, so convert to 0-indexed
            seasons = [int(s) for s in seasons]
            seasons = [j-1 for j in seasons]
        mask = self.df.loc[self.df['season'].isin(seasons)]
        return mask

    def _postseason_filter_df(self, postseason):
        """
        Filter game data to postseason games only.
        """
        if postseason:
            mask = self.df.loc[self.df['isPostseason']==True]
            return mask
        else:
            return self.df

    def _team_filter_df(self, teams):
        """
        Filter game data on team(s).
        """
        mask = self.df.loc[(self.df['homeTeamNickname'].isin(teams)) | (self.df['awayTeamNickname'].isin(teams))]
        return mask

    def parse(self):
        """
        Parse game data to find interesting games matching reason param.

        Returns:
        List of tuples [(string description, dataframe table data)]
        """
        reason = self.reason
        result = []
        r2f = REASON2FUNCTION
        if reason in r2f.keys():
            # Return a list of tuples containing:
            # - description of table (reason games are interesting)
            # - table data (pandas dataframe)
            funcs = r2f[reason]
            for func in funcs:
                result.append(func(self.df))
        return result
