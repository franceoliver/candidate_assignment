import pandas as pd
import numpy as np
import os
import datetime as dt
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import math

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

    def phase_2(self):
        """

        :return:
        """
        df = self.df

        ## Data Cleansing
        # Replaceing all NaN values in 'AIRCONDITION', 'BALCONY', 'WARDROBE', 'GARDEN' with False
        for item in ['AIRCONDITION', 'BALCONY', 'WARDROBE', 'GARDEN']:
            df[item] = df[item].replace(True, 1)
            df[item] = df[item].replace(False, 0)
            df[item].fillna(0, inplace=True)

        # Estimating the number of bedrooms and bathrooms base off the nearest AREASIZE
        bedroom_index = df[['AREASIZE', 'BEDROOMS']].dropna().reset_index()
        bathroom_index = df[['AREASIZE', 'BATHS']].dropna().reset_index()
        def bed_match(row):
            if math.isnan(row['AREASIZE']):
                pass
            elif math.isnan(row['BEDROOMS']):
                value = row['AREASIZE']
                index = abs(bedroom_index['AREASIZE'] - value).idxmin()
                row['BEDROOMS'] = bedroom_index['BEDROOMS'].iloc[index]
            return row

        def bath_match(row):
            if math.isnan(row['AREASIZE']):
                pass
            elif math.isnan(row['BATHS']):
                value = row['AREASIZE']
                index = abs(bathroom_index['AREASIZE'] - value).idxmin()
                row['BATHS'] = bathroom_index['BATHS'].iloc[index]
            return row
        df = df.apply(bed_match, axis=1)
        df = df.apply(bath_match, axis=1)

        # Removing data where areasize is nan
        # df = df.loc[(~df['AREASIZE'].isna()) | (~df['ADDRESSLATITUDE'].isna()) | (~df['ADDRESSLONGITUDE'].isna())].reset_index()
        df = df.dropna(subset=['PROPERTYCATEGORY', 'SUBURB', 'STREETTYPE',
               'ADDRESSLATITUDE', 'ADDRESSLONGITUDE', 'AREASIZE', 'BEDROOMS', 'BATHS',
               'PARKING', 'AIRCONDITION', 'BALCONY', 'WARDROBE', 'GARDEN'])

        ## Regression set up
        # Creating dummy variables for str features
        df = df[['PROPERTYCATEGORY', 'SUBURB', 'STREETTYPE',
               'ADDRESSLATITUDE', 'ADDRESSLONGITUDE', 'AREASIZE', 'BEDROOMS', 'BATHS',
               'PARKING', 'AIRCONDITION', 'BALCONY', 'WARDROBE', 'GARDEN', 'SALE_PRICE']]

        df = pd.get_dummies(df, columns=['PROPERTYCATEGORY', 'SUBURB', 'STREETTYPE'], prefix="dmy", prefix_sep="*")


        # seperating df with sales_price data and without it
        sale_df = df.loc[~df['SALE_PRICE'].isna()].dropna() # Removing nas from the test data set.
        non_sale_df = df.loc[df['SALE_PRICE'].isna()]

        df_x = sale_df.drop('SALE_PRICE', axis=1)

        df_y = sale_df[['SALE_PRICE']]

        df_x.describe()

        reg = linear_model.LinearRegression()

        x_train, x_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.33, random_state=4)

        x_train.head()

        reg.fit(x_train, y_train)

        reg.coef_

        reg.predict(x_test)

        # mean square error
        np.mean((reg.predict(x_test) - y_test) ** 2)

        df['model_predict'] = reg.predict(df.drop('SALE_PRICE', axis=1))

        x = df.groupby("dmy*A").agg({'model_predict': ['sum']}).reset_index()



if __name__ == '__main__':
    assignment_obj = TakeHomeAssignment()
    phase1_result = assignment_obj.phase_1(year=2020, remove_duplicates=True)

