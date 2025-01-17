[![License: Apache-2.0](https://img.shields.io/badge/Apache-2.0%20v3-blue.svg)](https://github.com/fizban99/rich-dataframe-for-spyder/blob/master/LICENSE)

# Rich DataFrame for Spyder IDE

Create nice formatted dataframes to view within the Spyder environment:

![image](https://github.com/fizban99/rich-dataframe-for-spyder/raw/master/images/prettify_table.png)

# Installation
Just download the rich_dataframe folder or simply the rich_dataframe.py file and place it in your working folder.

Supports multilevel index and multilevel columns and displays the column types below the column names. Shows also basic statistics at the bottom of the table.

Spyder color support in the console is very limited, but enough to help differentiate the different information pieces.

Build on top of https://github.com/khuyentran1401/rich-dataframe and https://github.com/fomightez/rich-dataframe to use it within Spyder. Although Spyder has a nice Dataframe viewer, sometimes it is faster to pretty print the content on the console. The original functionality has been changed slightly and the parameters as well. 

# Usage
## Minimal example
```python
import pandas as pd
iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv').set_index('species', append=True)
prettify(iris)
    
```

## Parameters
* **df: pd.DataFrame**
The data you want to prettify
* **row_limit : int, optional**
    Number of rows to show, by default `20`
* **clear_console: bool, optional**
    Clear the console before printing the table, by default False to maintain previous console input/output. If this is set to True, the console is cleared.
* **force_jupyter: bool, optional**
    Assumes IPython and uses more than the 80 chars of the default console. Default True. 