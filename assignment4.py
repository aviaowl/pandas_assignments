import pandas as pd
from scipy.stats import ttest_ind

pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', None)

"""
Hypothesis: University towns have their mean housing prices less effected by recessions. 
Run a t-test to compare the ratio of the mean price of houses in university towns 
the quarter before the recession starts compared to the recession bottom.

Sources:
1. From the Zillow research data site there is housing data for the United States. 
    In particular the datafile for all homes at a city level, City_Zhvi_AllHomes.csv, 
    has median home sale prices at a fine grained level.
2. From the Wikipedia page on college towns is a list of university towns in the United States 
    which has been copy and pasted into the file university_towns.txt.
3. From Bureau of Economic Analysis, US Department of Commerce, 
    the GDP over time of the United States in current dollars (use the chained value in 2009 dollars), 
    in quarterly intervals, in the file gdplev.xls. For this assignment, only look at GDP data 
    from the first quarter of 2000 onward.
"""

states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National',
          'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana',
          'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho',
          'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan',
          'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico',
          'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa',
          'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana',
          'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California',
          'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island',
          'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia',
          'ND': 'North Dakota', 'VA': 'Virginia'}


def get_list_of_university_towns():
    """
    Returns a DataFrame of towns and the states they are in from the
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ],
    columns=["State", "RegionName"]  )

    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'.
    """
    with open('source/university_towns.txt') as cities:
        cities_dict = {}
        current_key = ''
        for row in cities.readlines():
            row = row.strip()
            if 'edit' in row:
                current_key = row.replace('[edit]', '')
            elif '(' in row:
                town = row[:row.index('(') - 1]
                cities_dict[town] = current_key
            else:
                cities_dict[row] = current_key

    df = pd.DataFrame.from_dict(cities_dict, orient='index').reset_index()
    df.columns = ['RegionName', 'State']
    df = df[['State', 'RegionName']]

    return df.sort_values(by=['State', 'RegionName'])


def prepare_gbp_data():
    """
    Return prepared data on USA GDP by quarters from 2000 to 2016.
    """
    df = pd.read_excel('source/gdplev.xls', skiprows=8, usecols='E:F', index_col=None, header=None)
    df.columns = ['Quarter', 'GDP']
    df['Year'] = pd.to_numeric(df['Quarter'].str.split(pat='q', expand=True)[0])
    df = df[df['Year'] >= 2000][['Quarter', 'GDP']]
    df['Diff'] = df['GDP'].diff()
    return df.reset_index()


def get_start_end():
    """
    Finds the start, and end of the recession, to avoid duplication of code in the appropriate methods.
    """
    df = prepare_gbp_data()
    start = df[(df['Diff'].shift(-1) < 0) & (df['Diff'] < 0)]
    df = df.iloc[start.index[0] - 1:].reset_index()
    end = df[(df['Diff'].shift(-1) > 0) & (df['Diff'] > 0)]
    df = df.iloc[:end.index[0] + 1]
    return df


def get_recession_start():
    """
    Returns the year and quarter of the recession start time as a
    string value in a format such as 2005q3
    """

    df = get_start_end()
    return df.iloc[0]['Quarter']


def get_recession_end():
    """
    Returns the year and quarter of the recession end time as a
    string value in a format such as 2005q3
    """
    df = get_start_end()
    return df.iloc[-1]['Quarter']


def get_recession_bottom():
    """
    Returns the year and quarter of the recession bottom time as a
    string value in a format such as 2005q3
    """
    df = get_start_end()
    return df[df['GDP'] == df['GDP'].min()]['Quarter'].values[0]


def convert_housing_data_to_quarters():
    """
    Converts the housing data to quarters and returns it as mean
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].

    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    """
    raw = pd.read_csv('source/City_Zhvi_AllHomes.csv')
    df = raw[['State', 'RegionName'] + list(raw.columns[51:])]
    df.loc[:, 'State'] = df['State'].map(states)
    df.set_index(["State", "RegionName"], inplace=True)
    df = df.groupby(pd.PeriodIndex(df.columns, freq='Q'), axis=1).mean()
    return df


def run_ttest():
    """
    First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values,
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence.

    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).
    """
    university_towns = get_list_of_university_towns().set_index('RegionName')
    all_houses = convert_housing_data_to_quarters().dropna()
    start_q = get_recession_start()
    bottom_q = get_recession_bottom()

    df = all_houses.copy()
    df['ratio'] = df[start_q] / df[bottom_q]

    unitown = df.loc[list(university_towns.index)]['ratio'].dropna()
    nonunitown = df.loc[list(set(df.index) - set(unitown)), :]['ratio'].dropna()
    tstat, p = tuple(ttest_ind(unitown, nonunitown))

    different = p < 0.05
    result = tstat < 0
    better = ["university town", "non-university town"]
    return different, p, better[result]


print(run_ttest())
