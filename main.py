import pandas as pd
import numpy as np
import os
import datetime as dt


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
        self.properties_df = pd.read_csv(os.getcwd() + '/DATA/properties.csv')
        self.transactions_df = pd.read_csv(os.getcwd() + '/DATA/transactions.csv')

        self.transactions_df['SALE_DATE'] = pd.to_datetime(self.transactions_df['SALE_DATE'], dayfirst=True)

        self.df = self.properties_df.merge(self.transactions_df, how='left', on='ID')

    def phase_1(self, year: str, remove_duplicates: bool) -> pd.DataFrame:
        """
        Working function for all phase 1 work

        '‘suburb B’ has the highest total property market value in 2020 among several elite suburbs
        (the ones in the provided data set).'

        H0: The statement is True
        H1: The statment is False

        :return:
        """
        # Filtering for only houses sold in 2020.
        df_year = self.df.loc[self.df['SALE_DATE'].dt.year == year]

        if remove_duplicates == True:
            # Checking for unique sales to ensure no properties are double counted for multiple sales in one year.
            unique_sales = df_year[['ID', "SALE_DATE"]].groupby("ID").count()
            more_than_one_sale_2020 = df_year.loc[df_year['ID'] == unique_sales.loc[unique_sales['SALE_DATE'] > 1].index[0]]
            print(f"***Property: {unique_sales.loc[unique_sales['SALE_DATE'] > 1].index[0]} "
                  f"was sold more than once in {year}****")

            # ASSUMPTION 1: Where a property has been sold more than once during the year. We will only include
            # their most recent sales price.
            df_year = df_year.sort_values(by='SALE_DATE').drop_duplicates(subset= ['ID'], keep='last')

        # Agregating by Suburb to get the total values as deterimined by sales price.
        phase1_result = df_year.groupby("SUBURB").agg({'SALE_PRICE': ['sum']}).reset_index()

        #Extracting our answer for phase 1
        answers = phase1_result[phase1_result[('SALE_PRICE', 'sum')] ==phase1_result[('SALE_PRICE', 'sum')].max()].reset_index(drop=True)
        print(f"Suburb {answers[('SUBURB', '')][0]} has the highest Total property market value in {year}"
                     f" with a value of ${answers[('SALE_PRICE', 'sum')][0]}")
        return phase1_result

if __name__ == '__main__':
    assignment_obj = TakeHomeAssignment()
    phase1_result = assignment_obj.phase_1(year=2020, remove_duplicates=True)

