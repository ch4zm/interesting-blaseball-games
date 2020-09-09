import time
import os
from rich.console import Console
from rich.table import Table
from .game_data import GameData
from .util import (
    sanitize_dale,
    get_league_division_team_data
)


NAMESTYLE_CHOICES = ['long', 'short', 'emoji']


class View(object):
    """
    Base class for view classes, so that they all have
    the same options variables available.
    """
    def __init__(self, options):
        self.nresults = options.n_results
        self.game_data = GameData(options)
        self.column_headers, self.nice_column_headers = self.assemble_column_headers(options)
        self.name_style = options.name_style
        self.teams = options.team  # not sanitized - contain unicode
        self.html = options.html

        # For table description
        self.options = options

        # If an output file is specified, check if it exists and if the path to it exists
        if options.output == '':
            self.output_file = None
        else:
            self.output_file = options.output
            if os.path.exists(self.output_file):
                print("WARNING: Overwriting an existing file %s"%(self.output_file))
                print("Waiting 5 seconds before proceeding")
                time.sleep(5)
                # Clear out the file
                with open(self.output_file, 'w') as f:
                    f.write("")
            else:
                output_file_path = os.path.abspath(os.path.dirname(self.output_file))
                if not os.path.exists(output_file_path):
                    raise Exception("Error: directory for output file (%s) does not exist!"%(output_file_path))

    def make_table(self):
        """Virtual method to make table(s)"""
        raise NotImplementedError("View class is a base class, do not call it directly")

    def table_description(self, reason):
        """
        Create table descriptions for each table, customizing
        based on filters the user provides
        """
        options = self.options
        if reason == 'blowout':
            desc = "Blowout games (games with high scores and high run differentials) "
        elif reason == 'shutout':
            desc = "Shutout games (games where the loser had zero runs) "
        elif reason == 'shame':
            desc = "Shame games (games where the loser was shamed) "
        elif reason == 'underdog':
            desc = "Underdog games (games where the underdog won with large run differential) "

        if options.season == 'all':
            desc += "for all time "
        else:
            if len(options.season)==1:
                desc += "for season %s "%("".join(options.season))
            else:
                desc += "for seasons %s "%(", ".join(options.season))

        if options.postseason :
            desc += "(postseason only) "

        # Remember: ALLTEAMS is sanitized for the command line, options.teams is desanitized (contains unicode)
        _, _, ALLTEAMS = get_league_division_team_data()

        # Sanitize unicode for comparison to ALLTEAMS
        # self.teams contains unicode for printing
        # teams is sanitized for comparison
        teams = [sanitize_dale(t) for t in self.teams]

        # Use the sanitized team names for comparison
        if len(self.team) == 1:
            # Use the desanitized team names for printing
            desc += "for the %s"%("".join(self.teams))
        elif len(set(ALLTEAMS) - set(teams)) == 0:
            desc += "for all teams"
        else:
            desc += "for the %s"%(", ".join(self.teams))

        return desc

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


class HtmlView(View):
    """
    Create a table and render it using Panda's to_html function
    """
    def make_table(self):
        tables = self.game_data.parse()
        for table in tables:
            reason, df = table
            desc = self.table_description(reason)
            cut = df[self.column_headers][:min(len(df), self.nresults)].copy()

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

            # If you don't have the right HTML head tag, the unicode won't display.
            # To print names without unicode, uncomment the block below:
            ### name_cols = [
            ###     'winningTeamName', 'winningTeamNickname', 
            ###     'losingTeamName', 'losingTeamNickname',
            ###     'homeTeamName', 'homeTeamNickname',
            ###     'awayTeamName', 'awayTeamNickname'
            ### ]
            ### for name_col in name_cols:
            ###     if name_col in cut.columns:
            ###         cut[name_col] = cut[name_col].apply(sanitize_dale)

            # Make everything in the dataframe a string
            cut = cut.applymap(str)

            # Rename df columns
            ren = {k: v for k, v in zip(self.column_headers, self.nice_column_headers)}
            cut.rename(columns = ren, inplace=True)

            # -----

            result = cut.to_html(justify='center', border=1, index=False)
            if self.output_file is None:
                print("<p>"+desc+"</p>\n")
                print("<br />")
                print(result)
                print("<br /><br />")
            else:
                with open(self.output_file, 'a') as f:
                    f.write("<p>"+desc+"</p>\n")
                    f.write("<br />\n")
                    f.write(result)
                    f.write("<br /><br />\n")

        if self.output_file is None:
            print("<p>Note: all days and seasons displayed are 1-indexed.</p>")
        else:
            with open(self.output_file, 'a') as f:
                f.write("\n<p>Note: all days and seasons displayed are 1-indexed.</p>\n")
            print("Wrote table HTML to file: %s"%(self.output_file))


class RichView(View):
    """
    Create a table and render it using rich
    """
    def make_table(self):
        """
        Get a list of DataFrames and descriptions, 
        and render them as tables with rich.
        """
        # Get dataframes and descriptions
        tables = self.game_data.parse()
        for table in tables:
            reason, df = table
            desc = self.table_description(reason)
            self._render_table(desc, df)

    def _render_table(self, description, df):
        """
        Render a table using rich
        """
        # Cut data to table data only
        cut = df[self.column_headers][:min(len(df), self.nresults)].copy()

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

        # -----

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
        print(description)
        console.print("\n\n")


class MarkdownView(View):
    """
    Create a table and render it as a Markdown table
    """
    # TODO: integrate some of the shared rich/markdown view functionality
    def make_table(self):
        """
        Get list of DataFrames and descriptions,
        and render each one as Markdown table
        """
        tables = self.game_data.parse()
        for table in tables:
            reason, df = table
            desc = self.table_description(reason)
            self._render_table(desc, df)

    def _render_table(self, description, df):
        """
        Render a table as a Markdown table
        """
        # Cut data to table data only
        cut = df[self.column_headers][:min(len(df), self.nresults)].copy()

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

        # -----

        # This string is the final table in Markdown format
        table = ""

        # Start header line
        table_header = "| "
        # Start separator line (controls alignment)
        table_sep = "| "
        for column_header, nice_column_header in zip(self.column_headers, self.nice_column_headers):
            table_header += "%s | "%(nice_column_header)
            if column_header=="losingScore" or column_header=="awayScore":
                # Justify losing/away scores to the right (opposite winning/home scores)
                table_sep += "------: | "
            elif self.name_style=="emoji" and column_header[-5:]=="Emoji":
                # Center emoji team name columns
                table_sep += ":------: | "
            else:
                table_sep += "------ |"

        table += table_header
        table += "\n"
        table += table_sep
        table += "\n"

        for i, row in cut.iterrows():
            table_row = "| "
            for val in row.values:
                table_row += "%s | "%(str(val))
            table += table_row
            table += "\n"

        # TODO
        # Something something, DRY
        # Something something, more pythonic
        if self.output_file is None:
            print("\n\n")
            print(description)
            print("\n")
            print(table)
            print("\n")
            print("\nNote: all days and seasons displayed are 1-indexed.")
        else:
            with open(self.output_file, 'a') as f:
                f.write("\n\n")
                f.write(description)
                f.write("\n")
                f.write(table)
                f.write("\n")
                f.write("\nNote: all days and seasons displayed are 1-indexed.")

