from rich.console import Console
from rich.table import Table
from .game_data import GameData


NAMESTYLE_CHOICES = ['long', 'short', 'emoji']


class View(object):
    def __init__(self, options):
        self.nresults = options.n_results
        self.game_data = GameData(options)
        self.column_headers, self.nice_column_headers = self.assemble_column_headers(options)
        self.name_style = options.name_style

    def make_table(self):
        """
        Get a list of DataFrames and descriptions, 
        and render them as tables with rich.
        """
        # Get list of [(description, dataframe)] tuples
        tables = self.game_data.parse()
        for table in tables:
            desc, df = table
            self.render_table(desc, df)

    def render_table(self, description, df):
        """
        Render a table using rich
        """
        # Cut data to table data only
        cut = df[self.column_headers][:min(len(df), self.nresults)].copy()

        # If description contains "underdog", 

        # Bump season and game numbers by one (zero-indexed in dataframe)
        # (Pandas is soooo intuitive)
        plusone = lambda x : x + 1
        new_season_column = cut['season'].apply(plusone)
        new_game_column = cut['day'].apply(plusone)
        cut = cut.assign(**{'season': new_season_column, 'day': new_game_column})

        # Format the isPostseason column for printing (empty space if not, else Y)
        postseason_lambda = lambda c: ' ' if c is False else 'Y'
        new_postseason_column = cut['isPostseason'].apply(postseason_lambda)
        cut = cut.assign(**{'isPostseason': new_postseason_column.values})

        # Format any column ending in "Emoji" as emoji (hope this works!)
        # (there must be a more efficient way to do this, but I really, really hate pandas now.)
        for column_header in self.column_headers:
            emoji_lambda = lambda x: chr(int(x, 16))
            if column_header[-5:]=='Emoji':
                new_column = cut[column_header].apply(emoji_lambda)
                cut = cut.assign(**{column_header: new_column})

        # Make everything in the dataframe a string
        cut = cut.applymap(str)

        console = Console()

        console.print("\n\n")

        table = Table(show_header=True, header_style="bold")

        for column_header, nice_column_header in zip(self.column_headers, self.nice_column_headers):
            if column_header=="losingScore" or column_header=="awayScore":
                # Justify losing/away scores to the right (opposite winning/home scores)
                table.add_column(nice_column_header, justify="right")
            elif self.name_style=="emoji" and column_header[-5:]=="Emoji":
                # Center emoji team name columns
                table.add_column(nice_column_header, justify="center")
            else:
                table.add_column(nice_column_header)

        for i, row in cut.iterrows():
            table.add_row(*row.values)

        console.print(table)
        console.print("\n")
        console.print(description)
        console.print("\n\n")

    def assemble_column_headers(self, options):
        """
        Create a list of column names to show in the final table.
        These should be in their correct final order.

        If organizing by winner/loser:
        Season | Game | Winning Pitcher | Winning Team | Winning Runs | Losing Runs | Losing Team | Losing Pitcher

        If organizing by home/away:
        Season | Game | Home Pitcher | Home Team | Home Runs | Away Runs | Away Team | Away Pitcher

        The column names are the dataframe column names,
        the nice column names are for printing.

        (pitcher columns are optional)
        """
        column_names = ['season', 'day', 'isPostseason']
        nice_column_names = ["Seas", "Day", "Post"]

        # Next columns will be winner/loser or home/away,
        # depending on the win_loss vs home_away options.
        if options.win_loss:

            # Winning pitcher
            if options.winning_pitcher:
                column_names.append('winningPitcherName')
                nice_column_names.append("WP")

            # Winning team name
            if options.name_style=='long':
                column_names.append('winningTeamName')
            elif options.name_style=='short':
                column_names.append('winningTeamNickname')
            elif options.name_style=='emoji':
                column_names.append('winningTeamEmoji')
            nice_column_names.append("Winner")

            # Winning team score
            column_names.append('winningScore')
            nice_column_names.append("Runs")

            # Losing team score
            column_names.append('losingScore')
            nice_column_names.append("Runs")

            # Losing team name
            if options.name_style=='long':
                column_names.append('losingTeamName')
            elif options.name_style=='short':
                column_names.append('losingTeamNickname')
            elif options.name_style=='emoji':
                column_names.append('losingTeamEmoji')
            nice_column_names.append("Loser")

            # Losing pitcher
            if options.losing_pitcher:
                column_names.append('losingPitcherName')
                nice_column_names.append("LP")

        elif options.home_away:

            # Home pitcher
            if options.home_pitcher:
                column_names.append('homePitcherName')
                nice_column_names.append("Home P")

            # Home team name
            if options.name_style=='long':
                column_names.append('homeTeamName')
            elif options.name_style=='short':
                column_names.append('homeTeamNickname')
            elif options.name_style=='emoji':
                column_names.append('homeTeamEmoji')
            nice_column_names.append("Home")

            # Home team score
            column_names.append('homeScore')
            nice_column_names.append("Runs")

            # Away team score
            column_names.append('awayScore')
            nice_column_names.append("Runs")

            # Away team name
            if options.name_style=='long':
                column_names.append('awayTeamName')
            elif options.name_style=='short':
                column_names.append('awayTeamNickname')
            elif options.name_style=='emoji':
                column_names.append('awayTeamEmoji')
            nice_column_names.append("Away")

            # Away pitcher
            if options.away_pitcher:
                column_names.append('awayPitcherName')
                nice_column_names.append("Away P")

        return (column_names, nice_column_names)
