import pandas as pd
import numpy as np
import os

class TakeHomeAssignment:
    """
    Working script for take home assessment

    Exercise 2: Phase 1 and 2
    """
    def __init__(self):
        """
        init to load data sets

        Simple data format and join
        """
        properties_df = pd.read_csv(os.getcwd()+'/DATA/properties.csv')
        transactions_df = pd.read_csv(os.getcwd()+'/DATA/transactions.csv')

        transactions_df['SALE_DATE'] = pd.to_datetime(transactions_df['SALE_DATE'], dayfirst=True)

        df = properties_df.merge(transactions_df, how='left', on='ID')

