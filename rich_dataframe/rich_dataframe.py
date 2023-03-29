###--------------------CUSTOMIZED RICH-DATAFRAME-------------------------###
# Based, almost directly, on https://github.com/khuyentran1401/rich-dataframe 
# Building it in because it is small and hasn't been updated much in a while &
# most importantly because I want to customize how it handles the captioning.
# I put this in my fork of https://github.com/khuyentran1401/rich-dataframe now .
# SPECIFIC CUSTOMIZATIONS:
#-------------------------
# I don't want the caption describing how many rows or cols shown unless number 
# of rows or columns is larger than how many are shown.
# Plus, adding note to install rich.
# Plus, removing the animation to the 'beat' because it causes weird spacing
# in Jupyter and I had already turned the speed up so high because I wasn't
# interested in the animated aspect that the default rich-dataframe makes.
# To do this and get output to show up even when using `%run` in Jupyter,
# I had to define the color and style of the columns when first made instead
# of updating after using the beat, `_add_random_color()`, & `_add_style()`,
# AND DELETE `with Live()`.
# Plus, removed `_change_width()` section since I'm not seeing a difference
# without it when not running animation.
# Plus, I added a setting so you could just dislay in terminal or equivalent 
# in monochrome if you didn't like the color features Rich-dataframe adds
# but like the table styling it allows. More like a plainer style but the 
# table still is easy to read in the terminal, like 
# https://stackoverflow.com/a/72747970/8508004 , but better because header 
# handled by rich-dataframe.
#-------------------------
# Development/Trouble-shooting cycle that worked best for developing my
# custom implementation:
# Starting a MyBinder session from 
# https://github.com/binder-examples/requirements and installing only `rich`
# and then runningan edited version of `example.py` from 
# https://github.com/fomightez/rich-dataframe allowed me to see I shouldn't 
# need `rich-dataframe` installed to get run `%run example.py` to show the 
# output in a JupyterLab cell. EDITS: `example.py` had the entire 
# `rich_dataframe.py` contents placed in it. I also changed what data it uses
# because it was annoying to get the large data it used and I wanted a 
# dataframe I was familiar with. I used the iris dataset that's built into 
# seaborn, see 
# https://github.com/mwaskom/seaborn-data . `iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')` or 
# !curl -OL https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv 
# can be used to use it with pandas or get it, respecitivey.  
# I didn't want to install seaborn to keep things simple in the session. Note that 
# `rich-dataframe` didn't seem to disply `iris` dataframe with the settings 
# in `example.py`  and so I further changed `example.py` to remove
# the reference to `first_rows` and `first_cols=False`.
# Then I could edit the top section from `rich_dataframe.py` to see what 
# could be removed to allow display of a static dataframe.
#-------------------------
# Adding this in this section of my script so only need rich installed if
# using command line. Use of the main function directly wouldn't necessarily
# need the code handling printng the dataframe in the terminal and so best
# rich not required in such cases so not asking user to install something
# that isn't used.
try:
    from rich import print
    from rich.text import Text
    from rich.align import Align
    from rich.color import Color
except ImportError:
    sys.stderr.write("Run `pip install rich` on your command line "
        "or if\nusing in a Jupyter notebook, run `%pip install rich`"
        ", without the tick marks.\n**EXITING.**.\n")
    sys.exit(1)
from rich.box import MINIMAL, SIMPLE, SIMPLE_HEAD, SQUARE
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.measure import Measurement
from rich.table import Table
import pandas as pd
import numpy as np
import math


# define a function to round to a specified number of significant digits
def round_sig(x, sig=3):
    if not isinstance(x, float) or x==0:
        return x
    else:
        try:
            return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)
        except:
            try:
               if np.isnan(x) or np.isinf(x):
                   return x
            except:
                try:
                    if np.isinf(x):
                        return x
                except:
                    pass
            return x

def supports_nan(dtype):
    try:
        # Check if an instance of the provided type can represent NaN
        instance = dtype()
        if math.isnan(instance + float('nan')):
            return True
    except (TypeError, ValueError):
        pass
    return False


def supports_inf(dtype):
    try:
        # Check if an instance of the provided type can represent NaN
        instance = dtype()
        if math.isnan(instance + float('inf')):
            return True
    except (TypeError, ValueError):
        pass
    return False


console = None
# COLORS = ["cyan", "magenta", "red", "green", "blue", "purple"]
class DataFramePrettify:
    """Create animated and pretty Pandas DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        The data you want to prettify
    row_limit : int, optional
        Number of rows to show, by default 20
    col_limit : int, optional
        Number of columns to show, by default 10
    clear_console: bool, optional
         Clear the console before printing the table, by default True. If this is set to False the previous console input/output is maintained
    """
    def __init__(
        self,
        df_input: pd.DataFrame,
        row_limit: int = 20,
        col_limit: int = 10,
        clear_console: bool = True,
        force_jupyter= False,
    ) -> None:
        global console
        console = Console(force_jupyter=force_jupyter)
        if 2 * row_limit < df_input.shape[0]:
            df = pd.concat([df_input[:row_limit], df_input[-row_limit:]], axis=0) 

        else:
            df = df_input[:]
            row_limit= 2*row_limit
        

        self.index_cols = df.index.nlevels
        df = df.reset_index()
        # df.values converts ints to float for no reason.
        df_dict = df.to_dict()
        self.rows = [[df_dict[col][i] for col in df_dict.keys()] for i in range(df.shape[0])]
        self.len_df = len(df)
        self.len_df_columns = len(df.columns)
        self.table = Table(show_footer=True)
        self.table.title = Align.left(f"\n[white italic][{df_input.shape[0]} rows x {df_input.shape[1]} columns][/white italic]")

        self.dtypes = df.dtypes
        self.row_limit = row_limit
        self.col_limit = col_limit
        self.clear_console = clear_console
        

        if type(df.columns[0]) == tuple:
            # Multilevel column
            column_names = ['\n'.join([str(c) for c in col]) for col in df.columns[:col_limit]]
            self.columns =[f"{name}\n[italic cyan]<{dtype}>[/cyan italic]" 
                           for name, dtype in zip(column_names, df.dtypes[:col_limit])]
        else:
            self.columns =[f"{col}\n[italic cyan]<{dtype}>[/cyan italic]" for col, dtype in zip(df.columns[:col_limit], df.dtypes[:col_limit])]
        self.counts = list(df_input.iloc[:,:col_limit].count())    
        self.maxs=[]
        self.mins=[]
        for col in range(col_limit):
            try:
                max_value = round_sig( list(df_input.iloc[:,col:col+1].max(numeric_only=False))[0])
            except:
                self.maxs.append("<mixed types>")
                self.mins.append("<mixed types>")
            else:
                self.maxs.append(max_value)
                min_value = round_sig(list(df_input.iloc[:,col:col+1].min(numeric_only=False))[0])
                self.mins.append(min_value)
                
        # self.mins = [round_sig(x) for x in list(df_input.iloc[:,:col_limit].min(numeric_only=False))]
        # self.means = [round_sig(x) for x in list(df_input.iloc[:,:col_limit].mean(numeric_only=True)) ]
        self.means = [round_sig(df_input.iloc[:,col].mean()) if not df_input.iloc[:,col:col+1].select_dtypes(include=['number']).empty else "n/a"
                      for col in range(col_limit)]
        self.nuniques = list(df_input.iloc[:,:col_limit].nunique()) 
        

        
        if self.clear_console:
            console.clear()

    def _add_columns(self):
        for i,col in enumerate(self.columns):
            self.table.add_column(str(col))
            # else:
            #     color4col = COLORS[i % self.num_colors]# based on https://github.com/khuyentran1401/rich-dataframe/blob/fff92c5fb735babcec580b88ef94b9325b5b8558/rich_dataframe/rich_dataframe.py#L110
            #     self.table.add_column(str(col),style="bold "+color4col, header_style="bold "+color4col,) # based on https://rich.readthedocs.io/en/stable/tables.html#tables 
            #     # and https://github.com/khuyentran1401/rich-dataframe/blob/fff92c5fb735babcec580b88ef94b9325b5b8558/rich_dataframe/rich_dataframe.py#L110


    def _add_footer(self):
       for i,col in enumerate(self.columns):
           if i ==self.index_cols-1:
               self.table.columns[i].footer = Align.right("[blue]count\nmax\nmin\nmean\nunique[/blue]")
           elif i<self.index_cols-1:
               self.table.columns[i].footer =""
           else:
               self.table.columns[i].footer = Align.right("[blue]" + str(self.counts[i-self.index_cols]) + "\n" +
                                               str(self.maxs[i-self.index_cols]) + "\n" +
                                               str(self.mins[i-self.index_cols]) + "\n" +
                                               str(round_sig(self.means[i-self.index_cols],3) ) + "\n" +
                                               str(self.nuniques[i-self.index_cols]) + "[/blue]")
                   
   
    
    def format_field(self, item):
        if supports_nan(type(item)) and np.isnan(item):
            return "[red]nan[/red]"
        elif supports_inf(type(item)) and np.isinf(item):
            return "[red]inf[/red]"
        else:
            return str(round_sig(item))
    
    def _add_rows(self):
        
        empty_row = ["...",] *min(self.col_limit,  len(self.rows[0]))
        for idx, row in enumerate(self.rows):
            row = row[: self.col_limit]
            if idx == self.row_limit:
                self.table.add_row(*empty_row)
            
            row = [self.format_field(item) for item in row]
            for i in range(self.index_cols):
                row[i] = f"[white]{row[i]}[/white]"
            self.table.add_row(*list(row))
            
    def _move_text_to_right(self):
        for i in range(len(self.table.columns)):
            if self.dtypes[i] != object:
                self.table.columns[i].justify = "right"
            else:
                self.table.columns[i].justify = "left"
    def _adjust_box(self):
        for box in [SIMPLE_HEAD, SIMPLE, MINIMAL, SQUARE]:
            self.table.box = box
            
    def _dim_row(self):
        self.table.row_styles = ["none", "dim"]
        
    def _adjust_border_color(self):
        pass
        
    def _add_caption(self):
        row_text = "first and last"
        col_text = "first and last"

        if (self.len_df > self.row_limit) and (self.len_df_columns > self.col_limit):
            self.table.caption = f"Only the [magenta] {row_text} {self.row_limit} rows[/magenta] and the [bold green not dim]{col_text} {self.col_limit} columns[/bold green not dim] are shown here."
        elif self.len_df > self.row_limit:
            self.table.caption = f"Only the [magenta] {row_text} {self.row_limit} rows[/magenta] are shown here."
        elif self.len_df_columns > self.col_limit:
            self.table.caption = f"Only the [bold green not dim]{col_text} {self.col_limit} columns[/bold green not dim] are shown here."

    def prettify(self):
        self._add_columns()
        self._add_rows()
        self._add_footer()
        self._move_text_to_right()
        self._adjust_border_color()
        self._add_caption()
        console.print(self.table) # based on https://rich.readthedocs.io/en/stable/tables.html#tables and https://stackoverflow.com/a/72747970/8508004
        return self.table
def prettify(
    df: pd.DataFrame,
    row_limit: int = 10,
    col_limit: int = 10,
    clear_console: bool = False,
    force_jupyter: bool = True,
):
    """Create animated and pretty Pandas DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        The data you want to prettify
    row_limit : int, optional
        Number of rows to show, by default 10
    col_limit : int, optional
        Number of columns to show, by default 10
    clear_console: bool, optional
        Clear the console before priting the table, by default True. If this is set to false the previous console input/output is maintained.
    """
    if isinstance(df, pd.DataFrame) or isinstance(df, pd.DataFrame):
        DataFramePrettify(
            df, row_limit, col_limit, clear_console,  force_jupyter
        ).prettify()

    else:
        # In case users accidentally pass a non-datafame input, use rich's 
        # print instead
        print(df)
###---------------END OF CUSTOMIZED RICH-DATAFRAME-----------------------###
