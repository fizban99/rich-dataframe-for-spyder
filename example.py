import pandas as pd

from rich_dataframe import prettify

if __name__ == "__main__":

    iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv').set_index('species', append=True)
    prettify(iris)