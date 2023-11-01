#Imports
import pandas as pd
import nfl_data_py as nfl
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup as bs 
import requests as rq

#Prompts user to enter player name in certain format 

def get_player_name():
    #Will continue to reprompt until format is correct
    while True:
        player = input('What Wide Receiver are you looking for? Please enter full name. (Ex: Justin Jefferson)\n')


        if all(word.istitle() and word.isalpha() for word in player.split()):
            break
        else:
            print('Invalid player name. Please reenter only using letters and check your spelling/capitalization')
    return player




#Prompts user to enter defense name in certain format 
def get_defense():
    #Pull team descriptor data
    team_desc = nfl.import_team_desc() 
    #Turn team name column to list
    list_of_teams = team_desc['team_name'].values.tolist() 
    #Will continue to reprompt until format is correct
    while True: 
        defense = input('What defense are they playing? (Ex. Detroit Lions)\n')

        if defense in list_of_teams:
            break
        else:
            print('Invalid team name. Check Spacing and Spelling.')
    return defense 



#Scrape defensive stats from profootballreference from years indicated in main prompt
#Utilizes requests to request html status if successful (stats code 200) bs4 is prompted to parse html
#If request fails return status code 
#Updates automatically when profootballreference updates
def fetch_defensive_stats(my_years):
    #Create data frame to append smaller ones to
    defensive_rankings = pd.DataFrame()
    #URL request for years indicated 
    for year in my_years:
        
        url = 'https://www.pro-football-reference.com'

            
        response = rq.get(url + '/years/' + str(year) + '/fantasy-points-against-WR.htm#fantasy_def')

        #If status success run parser
        if response.status_code == 200:
                
            soup = bs(response.text, 'html.parser')

                
            table = soup.find('table', {'id': 'fantasy_def'})

                
            df = pd.read_html(str(table))[0]

            #Multi Index to Single Index Dataframe
            df.columns = df.columns.get_level_values(-1)

            #Create Yards Per Game Column and Defensive Rank Column
            #Rank based on Yards Per Game in given year 
            df['Year'] = year
            df['YPG'] = df['Yds']/df['G']
            df = df.sort_values(by=['YPG'], ascending=True)
            df['Def_Rank'] = df['YPG'].rank(method='dense').astype(int)
            df = df.drop(columns = ['FantPt', 'DKPt', 'FDPt',
        'FantPt', 'DKPt', 'FDPt'])

            #Append to rankings dataframe
            defensive_rankings = pd.concat([defensive_rankings, df])

            
        #URL Request Fail
        else:
            print("Failed to retrieve the webpage. Status code:", response.status_code)
    return defensive_rankings

#Pull player schedule using nfl_data_py web scraping function
def fetch_player_schedules(player, my_years):
    tbl = nfl.import_weekly_pfr('rec', my_years)
    tbl = tbl[tbl['pfr_player_name'].str.contains(player) == True]
    #Drop unnessary columns
    tbl = tbl.drop(columns = ['game_id', 'pfr_game_id', 'game_type','pfr_player_id','rushing_broken_tackles', 'receiving_broken_tackles', 'passing_drops','passing_drop_pct', 'receiving_drop', 'receiving_drop_pct','receiving_int', 'receiving_rat'])
    return tbl

#Pull Wide Receiver stats from nfl_data_py data based on years 
#Updates automatically when nfl_data_py updates
def fetch_WR_stats(player, my_years):
    #Indicate columns wanted
    my_cols = ['position','player_display_name','recent_team','season','week', 'targets', 'target_share', 'receptions',  'receiving_yards', 'opponent_team']
    my_tbl = nfl.import_weekly_data(my_years, my_cols, downcast = True)
    #Isolate to just wide receivers
    my_tbl = my_tbl[my_tbl['position'].str.contains('WR') == True]
    #Isolate further to table only containing player name
    my_tbl= my_tbl[my_tbl['player_display_name'].str.contains(player) == True]
    return my_tbl

#Pull nfl team abbreviations data to help merge tables later
def fetch_team_abbreviations():
    team_abrv = nfl.import_team_desc()
    team_abrv = team_abrv[['team_name','team_abbr']]
    #Slightly changed data frame to include Washington Football Team due to changed team name in 2022
    team_abrv.at[32, 'team_name'] = 'Washington Football Team'
    team_abrv.at[32,'team_abbr'] = 'WAS'
    return team_abrv

#Change column names for all tables to make merging easier 
def manipulate_tables(team_abrv, my_tbl, defensive_rankings, tbl):
    team_abrv = team_abrv.rename(columns = {
                'team_name' : 'Opponent', 
                'team_abbr' : 'Abbreviation'})


    my_tbl = my_tbl.rename(columns = {
                'position' : 'Position', 
                'player_display_name': 'Name', 
                'recent_team' : 'Team', 
                'season' : 'Season', 
                'week' : 'Week',
                'targets' : 'Targets', 
                'target_share' : 'Target Share', 
                'receptions' : 'Receptions', 
                'receiving_yards' : 'Receiving Yards',
                'opponent_team' : 'Opponent'})

    tbl = tbl.rename(columns = {
                'season' : 'Season', 
                'week' : 'Week', 
                'team' : 'Team', 
                'opponent' : 'Opponent', 
                'pfr_player_name' : 'Name'})

    defensive_rankings = defensive_rankings.rename(columns = {
                    'Tm': "Opponent", 
                    'G' : 'Games', 
                    'Tgt' : 'Targets Allowed', 
                    'Rec' : 'Receptions Allowed', 
                    'Yds' : 'Receiving Yards Allowed', 
                    'TD' : 'Touchdowns Allowed', 
                    'Year': 'Season', 
                    'YPG' : 'Yards Allowed Per Game', 
                    'Def_Rank' : 'Defense Rank'})

    #Merge schedule with wide receiver stats
    merge1 = my_tbl.merge(tbl, on=['Season', 'Week', 'Team', 'Name'])
    #Merge defensive rankings with team abbreviations 
    merge2 = defensive_rankings.merge(team_abrv, on=['Opponent'])
    #Merge the baove two together to merge all needed tables
    regression_table = merge1.merge(merge2, left_on= ['Season','Opponent_y'], right_on= ['Season', 'Abbreviation'], how = "left")

    return regression_table



                                            
#Use defensive ranking table to find the current year rank of user inputted defense 
#Updates automatically when profootballreference updates
def fetch_current_def_rank(defensive_rankings, defense):

    curr_def_ranking = defensive_rankings.loc[(defensive_rankings['Year'] == 2023) & (defensive_rankings['Tm'] == defense), 'Def_Rank'].values[0]

    return curr_def_ranking
#------------------------------------------------------------------------------------------------------------------------------------------------------------------


def reshape_data(regression_table, curr_def_ranking):
    #Takes yards category and uses defensive rank as defensive indicator. 
    #Pulls the data in arrays and reshapes from scalar to 2 dimensional for lin reg
    y = regression_table['Receiving Yards'].values.reshape(-1,1)
    x = regression_table['Defense Rank'].values.reshape(-1,1)


    #Takes the def rank input and creates an array with it as an int then reshapes into 2D for lin reg
    def_arr = np.array([curr_def_ranking], dtype=np.float32)
    def_arr = def_arr.reshape(-1,1)
    
    return x, y, def_arr

#Linear Regression Model, Fits/Performs Regression
def lin_reg(x,y,def_arr):
    model = LinearRegression()  # create object for the class
    model.fit(x, y)  # perform linear regression

    return model

#Makes Predictions based on model and defensive rating
def predict(player, model, def_arr):
    prediction = model.predict(def_arr)
    #Prints full statement for user
    print(player,'will have about', prediction, ' receiving yards' )

#Visualizes data on chart using matplotlib and tkinter backend
def visualize(x,y,regression_table):

    #Create scatter plot
    plt.scatter(x, y)
    #Create trendline
    trend_line = model.predict(x)

    #Plot points and line
    plt.plot(x, trend_line, color='red', label='Trend Line')

    #Label and Show chart
    plt.xlabel('Defense Rank')
    plt.ylabel('Receiving Yards')
    plt.legend()
    plt.show()



#main
if __name__ == "__main__":
    player = get_player_name()
    defense = get_defense()

    #Years Range
    my_years = list(range(2021, 2024))

    defensive_rankings = fetch_defensive_stats(my_years)
    player_schedules = fetch_player_schedules(player, my_years)
    player_stats = fetch_WR_stats(player, my_years)
    team_abbreviations = fetch_team_abbreviations()

    regression_table = manipulate_tables(team_abbreviations, player_stats, defensive_rankings, player_schedules)

    curr_def_ranking = fetch_current_def_rank(defensive_rankings, defense)

    x, y, def_arr = reshape_data(regression_table, curr_def_ranking)

    model = lin_reg(x, y, def_arr)

    predict(player, model, def_arr)

    visualize(x, y, regression_table)

