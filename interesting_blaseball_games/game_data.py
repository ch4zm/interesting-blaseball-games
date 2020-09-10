import os
import pandas as pd
from .util import GAMES_DATA_JSON, root_path, data_path


def blowout(df):
    """
    Filter the dataframe of game data on blowouts
    (games with the largest run differential).
    Returns: tuple (string reason, dataframe tabledata)
    """
    reason = 'blowout'
    filt = df.sort_values(['winningScore', 'runDiff'], ascending=[False, False])
    return (reason, filt)


def shutout(df):
    """
    Filter the dataframe of game data on shutouts
    (games where one team has zero runs).
    Returns: tuple (string reason, pd dataframe)
    """
    reason = 'shutout'
    filt = df.loc[df['losingScore']==0]
    filt = filt.sort_values('runDiff', ascending=False)
    return (reason, filt)


def shame(df):
    """
    Filter the dataframe of game data on shame
    (games where one team was shamed).

    Returns: tuple (string reason, pd dataframe)
    """
    reason = 'shame'
    filt = df.loc[df['shame']==True]
    filt = filt.sort_values('runDiff', ascending=False)
    return (reason, filt)


def underdog(df):
    """
    Filter the dataframe of game data on underdog wins
    (games where the team with lower odds won).
    Returns: tuple (string reason, pd dataframe)
    """
    reason = 'underdog'
    filt = df.loc[df['winningOdds']<0.5]
    filt = filt.sort_values('runDiff', ascending=False)
    return (reason, filt)


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

        # Save options
        self.options = options

        # Drop tie games
        self.df = self._filter_ties()

        # Fiter data based on user configuration
        self.df = self._season_filter_df(options.season)
        self.df = self._postseason_filter_df(options.postseason)
        self.df = self._team_filter_df(options.team)

        # Add new columns
        self._add_columns()

    def _add_columns(self):
        """Add any additional columns we want as part of the View class"""
        # Add the score: homeAwayScore and winningLosingScore
        wl_score_lambda = lambda x: "%d - %d"%(x['winningScore'], x['losingScore'])
        import pdb; pdb.set_trace()
        wl_score_col = self.df[['winningScore', 'losingScore']].apply(wl_score_lambda, axis=1)
        self.df = self.df.assign(**{'winningLosingScore': wl_score_col.values})

        ha_score_lambda = lambda x: "%d - %d"%(x['homeScore'], x['awayScore'])
        ha_score_col = self.df[['homeScore', 'awayScore']].apply(ha_score_lambda, axis=1)
        self.df = self.df.assign(**{'homeAwayScore': ha_score_col.values})

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
        reason = self.options.reason
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
