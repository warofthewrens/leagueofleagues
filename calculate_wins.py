from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np
import math
from scipy import stats

nfl_teams = set(['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle',
                    'dal', 'den', 'det', 'htx', 'gnb', 'clt', 'jax', 'kan', 'rai',
                    'sdg', 'ram', 'mia', 'min', 'nwe', 'nor', 'nyg', 'nyj',
                    'phi', 'pit', 'sfo', 'sea', 'tam', 'oti', 'was'])

nba_teams = set(['ATL', 'BOS', 'NJN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET',
                 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
                 'NOH', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS',
                 'TOR', 'UTA', 'WAS'])

nhl_teams = set(['ANA', 'PHX', 'BOS', 'BUF', 'CGY', 'CAR', 'CHI', 'COL',
                 'CBJ', 'DAL', 'DET', 'EDM', 'FLA', 'LAK', 'MIN', 'MTL',
                 'NSH', 'NJD', 'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SJS',
                 'STL', 'TBL', 'TOR', 'VAN', 'VEG', 'WSH', 'WPG'])

def r2(x,y):
    return stats.pearsonr(x, y)[0]**2

def plot_win_data(win_df, year_over_year_df, xlim, xrsq, yrsq, ct, win_title, yoy_title):
    sns.histplot(data=win_df, x = 'wins', discrete=True)
    plt.xlim(-1, xlim + 1)
    sd = round(np.std(win_df['wins']), 5)
    annotation = f'Standard Deviation: {sd}'
    plt.annotate(annotation, (.63 * xlim, ct), fontsize = 16)
    plt.title(win_title, y = 0.94)
    plt.show()
    
    year_over_year_df['value'] = year_over_year_df['last_year'].astype(str) + year_over_year_df['current_year'].astype(str)
    year_over_year_df['value'] = pd.to_numeric(year_over_year_df['value'])
    year_over_year_df['counts'] = year_over_year_df['value'].map(year_over_year_df['value'].value_counts())
    g = sns.lmplot(x="last_year", y="current_year", hue="counts", data=year_over_year_df, fit_reg=False, palette='flare')
    sns.regplot(x="last_year", y="current_year", data=year_over_year_df, scatter=False, ax=g.axes[0, 0])
    #sns.lmplot(data=year_over_year_df, x='last_year', y='current_year')
    plt.annotate('r^2 value:' + str(round(r2(year_over_year_df['last_year'], year_over_year_df['current_year']), 5)), (xrsq, yrsq), fontsize = 14)
    plt.title(yoy_title, y = 0.97)
    plt.show()

def get_win_data(win_df):
    win_vals = []
    cur_vals = []
    prev_vals = []
    for name, data in win_df.iteritems():
        vals = data.values
        prev_val = None
        for val in vals:
            val = int(val)
            win_vals.append(val)
            if prev_val != None:
                cur_vals.append(val)
                prev_vals.append(prev_val)
            prev_val = val
    
    win_df = pd.DataFrame(win_vals, columns=['wins'])
    year_over_year_df = pd.DataFrame(list(zip(prev_vals, cur_vals)), columns=['current_year', 'last_year'])

    return win_df, year_over_year_df




def extract_nfl_wins_by_team(team):
    url = 'https://www.pro-football-reference.com/teams/'+ team + '/'

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    table = soup.find('table', attrs={'id':'team_index'})
    nfl_team_df = pd.read_html(table.prettify(), header=1)[0].head(25)
    nfl_team_df['Year'] = pd.to_numeric(nfl_team_df['Year'])
    nfl_team_df = nfl_team_df[(nfl_team_df['Year'] < 2020) & (nfl_team_df['Year'] > 1999)].dropna(axis='columns')

    win_df = pd.DataFrame(nfl_team_df['W'])
    return get_win_data(win_df)

def extract_nba_wins_by_team(team):
    url = 'https://www.basketball-reference.com/teams/' + team + '/'

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    table = soup.find('table', attrs={'id':team})
    nba_team_df = pd.read_html(table.prettify())[0].head(25)
    nba_team_df['Year'] = nba_team_df['Season'].str[:4]
    nba_team_df['Year'] = pd.to_numeric(nba_team_df['Year'])
    nba_team_df = nba_team_df[(nba_team_df['Year'] < 2019) & (nba_team_df['Year'] > 1998)].dropna(axis='columns')

    win_df = pd.DataFrame(nba_team_df['W'])
    return get_win_data(win_df)

def extract_nhl_wins_by_team(team):
    url = 'https://www.hockey-reference.com/teams/'+team+'/history.html'

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    table = soup.find('table', attrs={'id':team})
    nhl_team_df = pd.read_html(table.prettify())[0].head(25)
    nhl_team_df['Year'] = nhl_team_df['Season'].str[:4]
    nhl_team_df['Year'] = pd.to_numeric(nhl_team_df['Year'])
    nhl_team_df = nhl_team_df[(nhl_team_df['Year'] < 2019) & (nhl_team_df['Year'] > 1998)].dropna(axis='columns')

    win_df = pd.DataFrame(nhl_team_df['W'])
    return get_win_data(win_df)

def extract_mlb_wins():
    url = 'https://www.baseball-reference.com/leagues/MLB/index.shtml'

    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')

    table = soup.find('table', attrs={'id': 'teams_team_wins3000'})
    mlb_df = pd.read_html(table.prettify())[0]
    mlb_df = mlb_df[mlb_df['Year'].apply(lambda x: x.isnumeric())].dropna(subset=['Year'])
    mlb_df['Year'] = pd.to_numeric(mlb_df['Year'])
    mlb_df = mlb_df[(mlb_df['Year'] < 2020) & (mlb_df['Year'] > 1999)].dropna(axis='columns')
    mlb_df = mlb_df.drop(['Year', 'G'], axis = 1)

    win_df, year_over_year_df = get_win_data(mlb_df)

    plot_win_data(win_df, year_over_year_df, 162, 110, 110, 15, 'Distribution of Wins for MLB teams since 2000', 'Year over year win correlation in the MLB since 2000')

def extract_nfl_wins():
    i = 0
    for team in nfl_teams:
        if i == 0:
            win_df, year_over_year_df = extract_nfl_wins_by_team(team)
        else:
            new_win_df, new_yoy_df = extract_nfl_wins_by_team(team)
            win_df = win_df.append(new_win_df, ignore_index=True)
            year_over_year_df = year_over_year_df.append(new_yoy_df, ignore_index=True)
        i+=1
    print(win_df)
    plot_win_data(win_df, year_over_year_df, 16, 14, 14, 60, 'Distribution of Wins for NFL teams since 2000', 'Year over year win correlation in the NFL since 2000')

def extract_nba_wins():
    i = 0
    for team in nba_teams:
        if i == 0:
            win_df, year_over_year_df = extract_nba_wins_by_team(team)
        else:
            new_win_df, new_yoy_df = extract_nba_wins_by_team(team)
            win_df = win_df.append(new_win_df, ignore_index=True)
            year_over_year_df = year_over_year_df.append(new_yoy_df, ignore_index=True)
        i+=1
    plot_win_data(win_df, year_over_year_df, 82, 65, 65, 20, 'Distribution of Wins for NBA teams since 1999', 'Year over year win correlation in the NBA since 1999')

def extract_nhl_wins():
    i = 0
    for team in nhl_teams:
        if i == 0:
            win_df, year_over_year_df = extract_nhl_wins_by_team(team)
        else:
            new_win_df, new_yoy_df = extract_nhl_wins_by_team(team)
            win_df = win_df.append(new_win_df, ignore_index=True)
            year_over_year_df = year_over_year_df.append(new_yoy_df, ignore_index=True)
        i+=1
    plot_win_data(win_df, year_over_year_df, 82, 55, 55, 20, 'Distribution of Wins for NHL teams since 1999', 'Year over year win correlation in the NHL since 1999')


#extract_mlb_wins()

extract_nfl_wins()
extract_nba_wins()
extract_nhl_wins()