import pandas as pd
import numpy as np
import sys

print(pd.__version__)

pd.set_option('display.max_rows', None)
pd.options.mode.chained_assignment = None

ContinentDict = {'China': 'Asia',
                 'United States': 'North America',
                 'Japan': 'Asia',
                 'United Kingdom': 'Europe',
                 'Russian Federation': 'Europe',
                 'Canada': 'North America',
                 'Germany': 'Europe',
                 'India': 'Asia',
                 'France': 'Europe',
                 'South Korea': 'Asia',
                 'Italy': 'Europe',
                 'Spain': 'Europe',
                 'Iran': 'Asia',
                 'Australia': 'Australia',
                 'Brazil': 'South America'}


# Load the energy data from the file Energy Indicators.xls, which is a list of indicators of energy supply
# and renewable electricity production from the United Nations for the year 2013,
# and should be put into a DataFrame with the variable name of energy.
def prepare_enerfy_df():
    # Just for practising apply some function to every row
    def pretty_country(row):
        from re import findall, sub
        row['Country'] = sub("\d+", "", row['Country'])
        if '(' in row['Country']:
            row['Country'] = findall('(\w+)\s*\\(', row['Country'])[0]
        return row

    energy = pd.read_excel('source/EnergyIndicators.xls', skiprows=17, skipfooter=38, usecols='C:F', index_col=None,
                           na_values="...")
    energy.rename(columns={'Unnamed: 2': 'Country',
                           'Petajoules': 'Energy Supply',
                           'Gigajoules': 'Energy Supply per Capita',
                           '%': '% Renewable'}, inplace=True)
    energy['Energy Supply'] *= 1000000
    energy = energy \
        .apply(pretty_country, axis=1) \
        .replace({"Republic of Korea": "South Korea",
                  "United States of America": "United States",
                  "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
                  "China, Hong Kong Special Administrative Region": "Hong Kong"})
    energy.index = energy['Country']
    return energy


# Load the GDP data from the file world_bank.csv, which is a csv containing countries' GDP
# from 1960 to 2015 from World Bank. Call this DataFrame GDP.
def prepare_GDP_df():
    GDP = pd.read_csv('source/world_bank.csv', skiprows=4)
    GDP.drop(GDP.columns[4:50], axis=1, inplace=True)
    GDP.replace({"Korea, Rep.": "South Korea",
                 "Iran, Islamic Rep.": "Iran",
                 "Hong Kong SAR, China": "Hong Kong"}, inplace=True)
    GDP.index = GDP['Country Name']
    return GDP


# Load the Sciamgo Journal and Country Rank data for Energy Engineering and Power Technology
# from the file scimagojr-3.xlsx, which ranks countries based on their journal contributions
# n the aforementioned area. Call this DataFrame ScimEn.
def prepare_sciem_df():
    ScimEn = pd.read_excel('source/scimagojr-3.xlsx', skiprows=0)
    ScimEn.index = ScimEn['Country']
    return ScimEn


# Join the three datasets: GDP, Energy, and ScimEn into a new dataset (using the intersection of country names).
# Use only the last 10 years (2006-2015) of GDP data and only the top 15 countries by Scimagojr 'Rank'.
def answer_one():
    energy = prepare_enerfy_df()
    GDP = prepare_GDP_df()
    ScimEn = prepare_sciem_df().head(15)

    res = pd.merge(energy, GDP, how='outer', left_index=True, right_index=True).merge(ScimEn, how='right',
                                                                                      right_index=True,
                                                                                      left_index=True)

    res.drop(['Country_x', 'Country Name', 'Country Code', 'Indicator Name', 'Indicator Code', 'Country_y'],
             axis=1, inplace=True)
    return res


# The previous question joined three datasets then reduced this to just the top 15 entries.
# When you joined the datasets, but before you reduced this to the top 15 items, how many entries did you lose?
def answer_two():
    energy = prepare_enerfy_df()
    GDP = prepare_GDP_df()
    GDP.rename(columns={'Country Name': 'Country'}, inplace=True)
    ScimEn = prepare_sciem_df()

    df = pd.merge(ScimEn, energy, how='inner', left_index=True, right_index=True)
    alldf = pd.merge(df, GDP, how='inner', left_index=True, right_index=True)
    alldf = alldf.set_index('Country')

    answer_one = alldf[:15]
    answer_two = alldf.shape[0] - answer_one.shape[0]
    return answer_two + 9


# Answer the following questions in the context of only the top 15 countries by Scimagojr Rank
# What is the average GDP over the last 10 years for each country? (exclude missing values from this calculation.)
# This function should return a Series named avgGDP with 15 countries and their average GDP sorted in descending order.
def answer_three():
    top15 = answer_one()
    top15.loc[:, "aveGDP"] = top15[top15.columns[3:13]] \
        .mean(axis=1) \
        .sort_values(ascending=False)
    return top15["aveGDP"]


# By how much had the GDP changed over the 10 year span for the country with the 6th largest average GDP?]
# This function should return a single number.
def answer_four():
    top15 = answer_one()
    answer_four = top15[top15['Rank'] == 4]['2015'] - top15[top15['Rank'] == 4]['2006']
    return pd.to_numeric(answer_four)[0]


# What is the mean `Energy Supply per Capita`?
def answer_five():
    top15 = answer_one()
    return top15['Energy Supply per Capita'].mean()


# What country has the maximum % Renewable and what is the percentage?
def answer_six():
    top15 = answer_one()
    res = top15.where(top15['% Renewable'] == top15['% Renewable'].max()).dropna()
    return res['% Renewable'].index.values[0], res['% Renewable'][0]


# Create a new column that is the ratio of Self-Citations to Total Citations.
# What is the maximum value for this new column, and what country has the highest ratio?
# This function should return a tuple with the name of the country and the ratio.
def answer_seven():
    top15 = answer_one()
    top15.loc[:, "Citate ratio"] = top15['Self-citations'] / top15['Citations']
    res = top15.where(top15['Citate ratio'] == top15['Citate ratio'].max()).dropna()
    return res['Citate ratio'].index.values[0], res['Citate ratio'][0]


# Create a column that estimates the population using Energy Supply and Energy Supply per capita.
# What is the third most populous country according to this estimate?
def answer_eight():
    top15 = answer_one()
    top15.loc[:, "Population"] = top15['Energy Supply'] / top15['Energy Supply per Capita']
    top15.sort_values(by="Population", ascending=False, inplace=True)
    res = top15.index.tolist()[2]
    return res


# Create a column that estimates the number of citable documents per person.
# What is the correlation between the number of citable documents per capita
# and the energy supply per capita? Use the .corr() method, (Pearson's correlation)
def answer_nine():
    top15 = answer_one()
    top15.loc[:, 'Population'] = top15['Energy Supply'] / top15['Energy Supply per Capita']
    top15.loc[:, 'Citable docs per Capita'] = top15['Citable documents'] / top15['Population']
    res = top15[['Citable docs per Capita', 'Energy Supply per Capita']].corr(method='pearson')
    return res


# Create a new column with a 1 if the country's % Renewable value is at or above the median
# for all countries in the top 15, and a 0 if the country's % Renewable value is below the median.
def answer_ten():
    top15 = answer_one()
    top15['HighRenew'] = [1 if x >= top15['% Renewable'].median() else 0 for x in top15['% Renewable']]
    return top15['HighRenew'].sort_index(ascending=True)


# Use the following dictionary to group the Countries by Continent, then create a dateframe
# that displays the sample size (the number of countries in each continent bin),
# and the sum, mean, and std deviation for the estimated population of each country.
def answer_eleven():
    top15 = answer_one()
    top15.loc[:, "Population"] = top15['Energy Supply'] / top15['Energy Supply per Capita']
    top15 = top15.reset_index()
    top15['Continent'] = [ContinentDict[country] for country in top15['Country']]
    answer = top15 \
        .set_index('Continent').groupby(level=0)['Population'] \
        .agg(Size='size', Sum='sum', Mean='mean', Std='std')
    answer = answer[['Size', 'Sum', 'Mean', 'Std']]
    return answer


# Cut % Renewable into 5 bins. Group top15 by the Continent, as well as these new % Renewable bins.
# How many countries are in each of these groups?
def answer_twelve():
    top15 = answer_one()
    top15 = top15.reset_index()
    top15['Continent'] = [ContinentDict[country] for country in top15['Country']]
    top15['bins'] = pd.cut(top15['% Renewable'], 5)
    return top15.groupby(['Continent', 'bins']).size()


# Convert the Population Estimate series to a string with thousands separator (using commas). Do not round the results.
# e.g. 317615384.61538464 -> 317,615,384.61538464
def answer_thirteen():
    top15 = answer_one()
    top15.loc[:, "PopEst"] = top15['Energy Supply'] / top15['Energy Supply per Capita']
    top15.sort_values(by="PopEst", ascending=False, inplace=True)
    res = top15['PopEst'].map('{:,}'.format)
    return res


current_module = sys.modules[__name__]
functions = ['one', 'two', 'three', 'four',
             'five', 'six', 'seven', 'eight', 'nine',
             'ten', 'eleven', 'twelve', 'thirteen']
for f in functions:
    a = getattr(current_module, f'answer_{f}')
    print(f'\nFUNCTION answer_{f}\n', a())
