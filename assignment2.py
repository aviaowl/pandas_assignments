import pandas as pd
import sys

pd.set_option('display.max_rows', None)
df = pd.read_csv('source/olympics.csv', index_col=0, skiprows=1)
census_df = pd.read_csv('source/census.csv')

"""
The following code loads the olympics dataset (olympics.csv), which was derrived from the Wikipedia entry on 
All Time Olympic Games Medals, and does some basic data cleaning.
"""

# data clearing
for col in df.columns:
    if col[:2] == '01':
        df.rename(columns={col: 'Gold' + col[4:]}, inplace=True)
    if col[:2] == '02':
        df.rename(columns={col: 'Silver' + col[4:]}, inplace=True)
    if col[:2] == '03':
        df.rename(columns={col: 'Bronze' + col[4:]}, inplace=True)
    if col[:1] == '№':
        df.rename(columns={col: '#' + col[1:]}, inplace=True)

names_ids = df.index.str.split('\s\(')  # split the index by '('
df.index = names_ids.str[0]  # the [0] element is the country name (new index)
df['ID'] = names_ids.str[1].str[:3]  # the [1] element is the abbreviation or ID (take first 3 characters from that)
df = df.drop('Totals')


# What is the first country in df?
def answer_zero():
    return df.iloc[0]


# Which country has won the most gold medals in summer games?
def answer_one():
    max_medals = df['Gold'].max()
    result_row = df[df['Gold'] == max_medals]
    return result_row.index[0]


# Which country had the biggest difference between their summer and winter gold medal counts?
def answer_two():
    df['Difference'] = abs(df['Gold.1'] - df['Gold.2'])
    max_diff = df['Difference'].max()
    result_row = df[df['Difference'] == max_diff]
    return result_row.index[0]


# Which country has the biggest difference between their summer gold medal counts
# and winter gold medal counts relative to their total gold medal count?
def answer_three():
    only_gold = df.where((df['Gold'] > 0) & (df['Gold.1'] > 0))
    only_gold = only_gold.dropna()
    return (abs((only_gold['Gold'] - only_gold['Gold.1']) / only_gold['Gold.2'])).idxmax()


# Write a function that creates a Series called "Points" which is a weighted value
# where each gold medal (Gold.2) counts for 3 points, silver medals (Silver.2) for 2 points,
# and bronze medals (Bronze.2) for 1 point.
# The function should return only the column (a Series object) which you created, with the country names as indices.
def answer_four():
    value = df['Gold.2'] * 3 + df['Silver.2'] + 2 + df['Bronze.2'] * 1
    points = pd.Series(value, index=df.index)
    return points


# Which state has the most counties in it?
# (hint: consider the sumlevel key carefully! You'll need this for future questions too...)
def answer_five():
    return census_df[census_df['SUMLEV'] == 50].groupby('STNAME')['COUNTY'].nunique().idxmax()


# Only looking at the three most populous counties for each state,
# what are the three most populous states (in order of highest population to lowest population)?
def answer_six():
    most_populous_counties = census_df \
        .sort_values('CENSUS2010POP', ascending=False) \
        .groupby('STNAME') \
        .head(3)
    return most_populous_counties[['STNAME', 'CTYNAME', 'CENSUS2010POP']] \
        .groupby('STNAME') \
        .sum() \
        .sort_values(
        'CENSUS2010POP', ascending=False).head(3).index.tolist()


# Which county has had the largest absolute change in population within the period 2010-2015?
def answer_seven():
    census_df.index = census_df['CTYNAME']

    new_df = census_df[census_df['SUMLEV'] == 50]
    years_list = new_df[
        ['POPESTIMATE2010', 'POPESTIMATE2011', 'POPESTIMATE2012', 'POPESTIMATE2013', 'POPESTIMATE2014',
         'POPESTIMATE2015']]
    return (years_list.max(axis=1) - years_list.min(axis=1)).idxmax()


# In this datafile, the United States is broken up into four regions using the "REGION" column.
# Create a query that finds the counties that belong to regions 1 or 2, whose name starts with 'Washington',
# and whose POPESTIMATE2015 was greater than their POPESTIMATE 2014.
# This function should return a 5x2 DataFrame with the columns = ['STNAME', 'CTYNAME']
# and the same index ID as the census_df (sorted ascending by index).
def answer_eight():
    filter0 = (census_df['REGION'] == 1) | (census_df['REGION'] == 2)
    filter1 = census_df['CTYNAME'].str.startswith('Washington')
    filter2 = census_df['POPESTIMATE2015'] > census_df['POPESTIMATE2014']
    new_df = census_df.where(filter0 & filter1 & filter2)
    return new_df[['STNAME', 'CTYNAME']].dropna()


current_module = sys.modules[__name__]
functions = ['zero', 'one', 'two', 'three', 'four',
             'five', 'six', 'seven', 'eight']
for f in functions:
    a = getattr(current_module, f'answer_{f}')
    print(f'\nFUNCTION answer_{f}\n', a())
