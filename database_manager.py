import sqlite3
import json
import collections
import unicodedata
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import sys

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

'''
================================================
NOTE: In all the places country_id = league_id
================================================
'''


def getAllCountries():
    query = "Select * from Country"
    cursor.execute(query)
    countries_to_be_shown = [1729, 4769, 7809, 10257, 21518]
    countries = []
    for row in cursor:
        if (row[0] in countries_to_be_shown):
            countries.append(row)
    return countries


def getAllLeaguesFromCountry(country_id):
    query = "Select * from League where country_id = ?"
    cursor.execute(query, (country_id,))
    leagues = []
    for row in cursor:
        leagues.append(row)
    return leagues


def getTeamsForSeason(league_id, season):
    match_table_query = "Select home_team_api_id, away_team_api_id from Match where season = ? and league_id = ?"
    cursor.execute(match_table_query, (season, league_id))
    team_ids = []
    team_ids = set(team_ids)
    for row in cursor:
        team_ids.add(row[0])
        team_ids.add(row[1])
    team_ids = list(team_ids)
    teams = []
    teams_query = "Select team_api_id, team_long_name, team_short_name from Team where team_api_id = ?"
    for team_id in team_ids:
        cursor.execute(teams_query, (team_id,))
        for row in cursor:
            teams.append(row)
    return teams


def getTeamLongAndShortNames(team_id):
    get_team_name_query = "Select team_long_name, team_short_name From Team Where team_api_id = ?;";
    cursor.execute(get_team_name_query, (team_id,))
    team_names = []
    for row in cursor:
        team_names.append(unicodedata.normalize('NFKD', row[0]).encode('ascii', 'ignore'))
        team_names.append(unicodedata.normalize('NFKD', row[1]).encode('ascii', 'ignore'))

    return team_names


# Returned dictionary is of the form <TeamId, [Position, Points, Wins, Draws, Losses, GF, GA, GD, CS, TeamId, Long name, short name]>
def getEndSeasonStatisticsOfTeamsForSeason(league_id, season):
    get_standings_query = "Select home_team_goal, away_team_goal, home_team_api_id, away_team_api_id From Match Where season = ? And league_id = ?;";
    all_standings = {}
    home_standings = {}
    away_standings = {}

    overall = []
    home = []
    away = []

    cursor.execute(get_standings_query, (season, league_id,))
    for row in cursor:
        homeTeamGoal = row[0]
        awayTeamGoal = row[1]
        homeTeamId = row[2]
        awayTeamId = row[3]

        if homeTeamId not in all_standings:
            all_standings[homeTeamId] = [0] * 12
        if awayTeamId not in all_standings:
            all_standings[awayTeamId] = [0] * 12

        if homeTeamId not in home_standings:
            home_standings[homeTeamId] = [0] * 12

        if awayTeamId not in away_standings:
            away_standings[awayTeamId] = [0] * 12

        home_team_result_list = all_standings[homeTeamId]
        away_team_result_list = all_standings[awayTeamId]

        only_home_result = home_standings[homeTeamId]
        only_away_result = away_standings[awayTeamId]

        home_team_result_list[9] = homeTeamId
        away_team_result_list[9] = awayTeamId

        only_home_result[9] = homeTeamId
        only_away_result[9] = awayTeamId

        if int(homeTeamGoal) > int(awayTeamGoal):
            home_team_result_list[2] += 1  # win for home team
            only_home_result[2] += 1
            home_team_result_list[1] += 3  # 3 points for home team
            only_home_result[1] += 3
            away_team_result_list[4] += 1  # loss for away team
            only_away_result[4] += 1
        elif int(awayTeamGoal) == int(homeTeamGoal):
            home_team_result_list[3] += 1  # draw for home team
            only_home_result[3] += 1
            home_team_result_list[1] += 1  # 1 point for home team
            only_home_result[1] += 1

            away_team_result_list[3] += 1  # draw for away team
            only_away_result[3] += 1
            away_team_result_list[1] += 1  # 1 point for away team
            only_away_result[1] += 1
        else:
            home_team_result_list[4] += 1  # loss for home team
            only_home_result[4] += 1

            away_team_result_list[2] += 1  # win for away team
            only_away_result[2] += 1
            away_team_result_list[1] += 3  # 3 points for away win
            only_away_result[1] += 3

        home_team_result_list[5] += int(homeTeamGoal)  # GF
        home_team_result_list[6] += int(awayTeamGoal)  # GA
        home_team_result_list[7] += (int(homeTeamGoal) - int(awayTeamGoal))

        only_home_result[5] += int(homeTeamGoal)
        only_home_result[6] += int(awayTeamGoal)
        only_home_result[7] += (int(homeTeamGoal) - int(awayTeamGoal))

        if int(homeTeamGoal) == 0:
            home_team_result_list[8] += 1
            only_home_result[8] += 1

        if int(awayTeamGoal) == 0:
            away_team_result_list[8] += 1
            only_away_result[8] += 1

        away_team_result_list[5] += int(awayTeamGoal)  # GF
        away_team_result_list[6] += int(homeTeamGoal)  # GA
        away_team_result_list[7] += int(awayTeamGoal) - int(homeTeamGoal)

        only_away_result[5] += int(awayTeamGoal)
        only_away_result[6] += int(homeTeamGoal)
        only_away_result[7] += (int(awayTeamGoal) - int(homeTeamGoal))

        all_standings[homeTeamId] = home_team_result_list
        all_standings[awayTeamId] = away_team_result_list

        home_standings[homeTeamId] = only_home_result
        away_standings[awayTeamId] = only_away_result

    sorted_all_standings = sorted(all_standings.items(), key=lambda k: (k[1][1], k[1][7]), reverse=True)
    print sorted_all_standings
    all_position = []
    for club in sorted_all_standings:
        all_position.append(club[0])

    for key, value in all_standings.iteritems():
        # Add position to each club
        pos = all_position.index(key)
        value[0] = pos + 1

        # Team names
        team_names = getTeamLongAndShortNames(key)
        value[10] = str(team_names[0])
        value[11] = str(team_names[1])

    print all_standings

    sorted_home_standings = sorted(home_standings.items(), key=lambda k: (k[1][1], k[1][7]), reverse=True)
    home_position = []
    for club in sorted_home_standings:
        home_position.append(club[0])
    # print home_standings
    # print home_position

    for key, value in home_standings.iteritems():
        pos = home_position.index(key)
        value[0] = pos + 1

        # Team names
        team_names = getTeamLongAndShortNames(key)
        value[10] = str(team_names[0])
        value[11] = str(team_names[1])

    # print home_standings

    sorted_away_standings = sorted(away_standings.items(), key=lambda k: (k[1][1], k[1][7]), reverse=True)
    away_position = []
    for club in sorted_away_standings:
        away_position.append(club[0])

    for key, value in away_standings.iteritems():
        pos = away_position.index(key)
        value[0] = pos + 1

        # Team names
        team_names = getTeamLongAndShortNames(key)
        value[10] = str(team_names[0])
        value[11] = str(team_names[1])

    # print away_standings

    attributes_names_list = ['Pos', 'Pts', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'CS', 'team_id', 'long_name', 'short_name']
    for key, value in all_standings.iteritems():
        dict_list = zip(attributes_names_list, value)
        dict_list = dict(dict_list)
        overall.append(dict_list)

    # print overall

    for key, value in home_standings.iteritems():
        dict_list = zip(attributes_names_list, value)
        dict_list = dict(dict_list)
        home.append(dict_list)

    for key, value in away_standings.iteritems():
        dict_list = zip(attributes_names_list, value)
        dict_list = dict(dict_list)
        away.append(dict_list)

    data = {}
    data['overall'] = overall
    data['home'] = home
    data['away'] = away
    json_data = json.dumps(data)

    return json_data


# <TeamId, [Position, Points, Wins, Draws, Losses, GF, GA, GD, CS, TeamId, Long name, short name]>
def getHistoryStatsForTeam(league_id, season, team_id):
    get_history_stats_for_team_query = "Select home_team_goal, away_team_goal, home_team_api_id, away_team_api_id " \
                                       "From Match Where season = ? And league_id = ? And (home_team_api_id = ? or away_team_api_id = ?);"
    cursor.execute(get_history_stats_for_team_query, (season, league_id, team_id, team_id))

    result_list = [0] * 12
    for row in cursor:
        homeTeamGoal = row[0]
        awayTeamGoal = row[1]
        homeTeamId = row[2]
        awayTeamId = row[3]

        team_id = team_id.strip()

        if team_id == str(homeTeamId):
            if int(homeTeamGoal) > int(awayTeamGoal):
                result_list[2] += 1  # win for home team
                result_list[1] += 3  # 3 points for home team
            elif int(awayTeamGoal) == int(homeTeamGoal):
                result_list[3] += 1  # draw for home team
                result_list[1] += 1  # 1 point for home team

            else:
                result_list[4] += 1  # loss for home team

            result_list[5] += int(homeTeamGoal)  # GF
            result_list[6] += int(awayTeamGoal)  # GA
            result_list[7] += (int(homeTeamGoal) - int(awayTeamGoal))

        elif team_id == str(awayTeamId):
            if int(homeTeamGoal) > int(awayTeamGoal):
                result_list[4] += 1  # loss for away team
            elif int(awayTeamGoal) == int(homeTeamGoal):

                result_list[3] += 1  # draw for away team
                result_list[1] += 1  # 1 point for away team
            else:
                result_list[2] += 1  # win for away team
                result_list[1] += 3  # 3 points for away win

            result_list[5] += int(awayTeamGoal)  # GF
            result_list[6] += int(homeTeamGoal)  # GA
            result_list[7] += int(awayTeamGoal) - int(homeTeamGoal)

    print result_list


def getStandingsDetailsForGameweek(league_id, season, gameweek):
    gameweek_details_query = "Select home_team_goal, away_team_goal, home_team_api_id, away_team_api_id, match_api_id From Match Where season = ? And league_id = ? And stage = ?;"
    cursor.execute(gameweek_details_query, (season, league_id, gameweek,))
    result = {}
    for row in cursor:
        homeTeamGoal = row[0]
        awayTeamGoal = row[1]
        homeTeamId = row[2]
        awayTeamId = row[3]
        match_id = row[4]

        # [pos, points, GD, match id, team id, oppn id, score, team short name, team long name, oppn short name, oppn long name]
        if homeTeamId not in result:
            result[homeTeamId] = [0] * 11
        if awayTeamId not in result:
            result[awayTeamId] = [0] * 11

        home_team_result_list = result[homeTeamId]
        away_team_result_list = result[awayTeamId]

        home_team_result_list[3] = match_id
        away_team_result_list[3] = match_id

        home_team_result_list[4] = homeTeamId
        away_team_result_list[4] = awayTeamId

        home_team_result_list[5] = awayTeamId
        away_team_result_list[5] = homeTeamId

        home_team_result_list[6] = str(homeTeamGoal) + "-" + str(awayTeamGoal)
        away_team_result_list[6] = str(homeTeamGoal) + "-" + str(awayTeamGoal)

        result[homeTeamId] = home_team_result_list
        result[awayTeamId] = away_team_result_list

    gameweek_details_query = "Select home_team_goal, away_team_goal, home_team_api_id, away_team_api_id From Match Where season = ? And league_id = ? And stage < ?;"
    cursor.execute(gameweek_details_query, (season, league_id, gameweek + 1,))
    for row in cursor:
        homeTeamGoal = row[0]
        awayTeamGoal = row[1]
        homeTeamId = row[2]
        awayTeamId = row[3]

        home_team_result_list = result[homeTeamId]
        away_team_result_list = result[awayTeamId]

        if int(homeTeamGoal) > int(awayTeamGoal):
            home_team_result_list[1] += 3  # 3 points for home team
        elif int(awayTeamGoal) == int(homeTeamGoal):
            home_team_result_list[1] += 1  # 1 point for home team
            away_team_result_list[1] += 1  # 1 point for away team
        else:
            away_team_result_list[1] += 3  # 3 points for away win

        home_team_result_list[2] += (int(homeTeamGoal) - int(awayTeamGoal))
        away_team_result_list[2] += int(awayTeamGoal) - int(homeTeamGoal)

        result[homeTeamId] = home_team_result_list
        result[awayTeamId] = away_team_result_list

    od = collections.OrderedDict(sorted(result.items()))

    return dict(od)


# teams = getTeamsForSeason("1729", "2014/2015")
# print teams

def getSeasonwideStandingsDetails(league_id, season):
    overall = []

    count = 0
    for i in range(1, 39):
        # if count > 0:
        #     break
        gameweek_result = []

        result = getStandingsDetailsForGameweek(league_id, season, i)

        sorted_result = sorted(result.items(), key=lambda k: (k[1][1], k[1][7]), reverse=True)
        all_position = []
        for club in sorted_result:
            all_position.append(club[0])

        for key, value in result.iteritems():
            # Add position to each club
            pos = all_position.index(key)
            value[0] = pos + 1

            # Add short and long names
            team_id = value[4]
            oppn_id = value[5]
            team_names = getTeamLongAndShortNames(team_id)
            oppn_names = getTeamLongAndShortNames(oppn_id)

            value[7] = str(team_names[0])
            value[8] = str(team_names[1])
            value[9] = str(oppn_names[0])
            value[10] = str(oppn_names[1])

        attributes_names_list = ['pos', 'points', 'GD', 'match_id', 'team_id', 'oppn_id', 'score', 'team_short_name',
                                 'team_long_name', 'oppn_short_name', 'oppn_long_name']
        for key, value in result.iteritems():
            dict_list = zip(attributes_names_list, value)
            dict_list = dict(dict_list)
            gameweek_result.append(dict_list)

        overall.append(gameweek_result)

        count = count + 1

    json_data = json.dumps(overall)
    print json_data
    return json_data


def getPlayersForTeamInSeason(season):
    getHomeAndAwayTeamIdsQuery = "Select home_team_api_id, away_team_api_id, home_player_1, home_player_2, " \
                                 "home_player_3, home_player_4, home_player_5, home_player_6, home_player_7, " \
                                 "home_player_8, home_player_9, home_player_10, home_player_11, away_player_1, " \
                                 "away_player_2, away_player_3, away_player_4, away_player_5, away_player_6, " \
                                 "away_player_7, away_player_8, away_player_9, away_player_10, away_player_11 " \
                                 "From Match Where season = ?";

    cursor.execute(getHomeAndAwayTeamIdsQuery, (season,))
    result = {}
    for row in cursor:
        home_team_id = row[0]
        away_team_id = row[1]

        if home_team_id not in result:
            result[home_team_id] = []
        if away_team_id not in result:
            result[away_team_id] = []

        home_team_list = result[home_team_id]
        away_team_list = result[away_team_id]

        for i in range(2, 13):
            player_id = row[i]
            if (player_id not in home_team_list):
                home_team_list.append(player_id)

        for i in range(13, 24):
            player_id = row[i]
            if (player_id not in away_team_list):
                away_team_list.append(player_id)

        result[home_team_id] = home_team_list
        result[away_team_id] = away_team_list

    return result


# Returned dictionary is of the form <TeamId, [Position, Points, Wins, Draws, Losses, GF, GA, GD, CS, TeamId, Long name, short name]>
def getEndSeasonStatisticsOfTeamForSeason(league_id, season, team_id):
    get_standings_query = "Select home_team_goal, away_team_goal, home_team_api_id, away_team_api_id From Match Where season = ? And league_id = ?;";
    all_standings = {}

    overall = []

    cursor.execute(get_standings_query, (season, league_id,))
    for row in cursor:
        homeTeamGoal = row[0]
        awayTeamGoal = row[1]
        homeTeamId = row[2]
        awayTeamId = row[3]

        if homeTeamId not in all_standings:
            all_standings[homeTeamId] = [0] * 12
        if awayTeamId not in all_standings:
            all_standings[awayTeamId] = [0] * 12

        home_team_result_list = all_standings[homeTeamId]
        away_team_result_list = all_standings[awayTeamId]

        home_team_result_list[9] = homeTeamId
        away_team_result_list[9] = awayTeamId

        if int(homeTeamGoal) > int(awayTeamGoal):
            home_team_result_list[2] += 1  # win for home team
            home_team_result_list[1] += 3  # 3 points for home team
            away_team_result_list[4] += 1  # loss for away team
        elif int(awayTeamGoal) == int(homeTeamGoal):
            home_team_result_list[3] += 1  # draw for home team
            home_team_result_list[1] += 1  # 1 point for home team

            away_team_result_list[3] += 1  # draw for away team
            away_team_result_list[1] += 1  # 1 point for away team
        else:
            home_team_result_list[4] += 1  # loss for home team

            away_team_result_list[2] += 1  # win for away team
            away_team_result_list[1] += 3  # 3 points for away win

        home_team_result_list[5] += int(homeTeamGoal)  # GF
        home_team_result_list[6] += int(awayTeamGoal)  # GA
        home_team_result_list[7] += (int(homeTeamGoal) - int(awayTeamGoal))

        if int(homeTeamGoal) == 0:
            home_team_result_list[8] += 1

        if int(awayTeamGoal) == 0:
            away_team_result_list[8] += 1

        away_team_result_list[5] += int(awayTeamGoal)  # GF
        away_team_result_list[6] += int(homeTeamGoal)  # GA
        away_team_result_list[7] += int(awayTeamGoal) - int(homeTeamGoal)

        all_standings[homeTeamId] = home_team_result_list
        all_standings[awayTeamId] = away_team_result_list

    sorted_all_standings = sorted(all_standings.items(), key=lambda k: (k[1][1], k[1][7]), reverse=True)
    all_position = []
    for club in sorted_all_standings:
        all_position.append(club[0])

    for key, value in all_standings.iteritems():
        # Add position to each club
        pos = all_position.index(key)
        value[0] = pos + 1

        # Team names
        team_names = getTeamLongAndShortNames(key)
        value[10] = str(team_names[0])
        value[11] = str(team_names[1])

    team_stats = all_standings[int(team_id)]

    attributes_names_list = ['Pos', 'Pts', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'CS', 'team_id', 'long_name', 'short_name']
    dict_list = zip(attributes_names_list, team_stats)
    dict_list = dict(dict_list)
    # overall.append(dict_list)
    return dict_list


# Player info
def getPlayerNameHeightWeight(player_id):
    player_name_query = "Select player_name, height, weight From Player Where player_api_id = ?;"
    cursor.execute(player_name_query, (player_id,))
    name = ""
    height = 170.0
    weight = 170
    for row in cursor:
        name = unicodedata.normalize('NFKD', row[0]).encode('ascii', 'ignore')
        height = row[1]
        weight = row[2]

    return name, height, weight

def getPlayerPosition(player_id):
    get_player_pos_query = "Select home_player_X1, home_player_X2, home_player_X3, home_player_X4, home_player_X5, home_player_X6, home_player_X7, home_player_X8, home_player_X9, home_player_X10, home_player_X11, home_player_Y1, home_player_Y2, home_player_Y3, home_player_Y4, home_player_Y5, home_player_Y6, home_player_Y7, home_player_Y8, home_player_Y9, home_player_Y10, home_player_Y11, away_player_X1, away_player_X2, away_player_X3, away_player_X4, away_player_X5, away_player_X6, away_player_X7, away_player_X8, away_player_X9, away_player_X10, away_player_X11, away_player_Y1, away_player_Y2, away_player_Y3, away_player_Y4, away_player_Y5, away_player_Y6, away_player_Y7, away_player_Y8, away_player_Y9, away_player_Y10, away_player_Y11, home_player_1, home_player_2, home_player_3, home_player_4, home_player_5, home_player_6, home_player_7, home_player_8, home_player_9, home_player_10, home_player_11, away_player_1, away_player_2, away_player_3, away_player_4, away_player_5, away_player_6, away_player_7, away_player_8, away_player_9, away_player_10, away_player_11 From Match Where season = ?;";
    cursor.execute(get_player_pos_query, ("2015/2016",))
    pos = "NA"
    for row in cursor:
        gameType = ""
        pos = 0

        homeBaseColumnName = "home_player_"
        awayBaseColumnName = "away_player_"

        # home
        for i in range(44, 55):
            result_player_id = row[i]
            if result_player_id == player_id:
                pos = i % 11
                gameType = "home"

        # away
        for i in range(55, 66):
            result_player_id = row[i]
            if result_player_id == player_id:
                pos = i % 11
                gameType = "away"

        y_pos = 0
        if gameType == "home":
            index = pos + 11
            y_pos = row[index]
        elif gameType == "away":
            index = pos + 33
            y_pos = row[index]

        y_pos = int(y_pos)
        if y_pos == 0:
            pos = "GK"
        elif y_pos > 0 and y_pos <= 6:
            pos = "DEF"
        elif y_pos > 6 and y_pos <= 8:
            pos = "MID"
        elif y_pos > 8:
            pos = "ST"

    return pos

def getPlayerAttributes():
    get_player_attributes_query = "Select date, overall_rating, potential, attacking_work_rate, defensive_work_rate, crossing, finishing, heading_accuracy, short_passing, volleys, dribbling, curve, free_kick_accuracy, long_passing, ball_control, acceleration, sprint_speed, agility, reactions, balance, shot_power, jumping, stamina, strength, long_shots, aggression, interceptions, positioning, vision, penalties, marking, standing_tackle, sliding_tackle, gk_diving, gk_handling, gk_kicking, gk_positioning, gk_reflexes, player_api_id From Player_Attributes;";
    cursor.execute(get_player_attributes_query)
    overall_rating = potential = attacking_work_rate = defensive_work_rate = crossing = finishing = heading_accuracy = short_passing = volleys = dribbling = curve = free_kick_accuracy = long_passing = ball_control = acceleration = sprint_speed = agility = reactions = balance = shot_power = jumping = stamina = strength = long_shots = aggression = interceptions = positioning = vision = penalties = marking = standing_tackle = sliding_tackle = gk_diving = gk_handling = gk_kicking = gk_positioning = gk_reflexes = 0
    attacking = defensive = physical = mental = technical = goalkeeping = overall_rating = 0
    attr_list = []
    complete_attr_list = []
    attr_dict = {}
    count = 0
    for row in cursor:

        # count = count + 1
        # if count > 100:
        #     break

        overall_rating = row[1]
        potential = row[2]
        attacking_work_rate = row[3]
        defensive_work_rate = row[4]
        crossing = row[5]
        finishing = row[6]
        heading_accuracy = row[7]
        short_passing = row[8]
        volleys = row[9]
        dribbling = row[10]
        curve = row[11]
        free_kick_accuracy = row[12]
        long_passing = row[13]
        ball_control = row[14]
        acceleration = row[15]
        sprint_speed = row[16]
        agility = row[17]
        reactions = row[18]
        balance = row[19]
        shot_power = row[20]
        jumping = row[21]
        stamina = row[22]
        strength = row[23]
        long_shots = row[24]
        aggression = row[25]
        interceptions = row[26]
        positioning = row[27]
        vision = row[28]
        penalties = row[29]
        marking = row[30]
        standing_tackle = row[31]
        sliding_tackle = row[32]
        gk_diving = row[33]
        gk_handling = row[34]
        gk_kicking = row[35]
        gk_positioning = row[36]
        gk_reflexes = row[37]
        player_id = row[38]

        if attacking_work_rate == "low":
            attacking_work_rate = 33
        elif attacking_work_rate == "medium":
            attacking_work_rate = 66
        elif attacking_work_rate == "high":
            attacking_work_rate = 99
        else:
            attacking_work_rate = 33

        if defensive_work_rate == "low":
            defensive_work_rate = 33
        elif defensive_work_rate == "medium":
            defensive_work_rate = 66
        elif defensive_work_rate == "high":
            defensive_work_rate = 99
        else:
            defensive_work_rate = 33

        if sliding_tackle == None:
            sliding_tackle = 40
        if acceleration == None:
            acceleration = 40
        if agility == None:
            agility = 40
        if sprint_speed == None:
            sprint_speed = 40
        if balance == None:
            balance = 40
        if jumping == None:
            jumping = 40
        if stamina == None:
            stamina = 40
        if strength == None:
            strength = 40
        if reactions == None:
            reactions = 40
        if aggression == None:
            aggression = 40
        if positioning == None:
            positioning = 40
        if interceptions == None:
            interceptions = 40
        if vision == None:
            vision = 40
        if potential == None:
            potential = 40
        if heading_accuracy == None:
            heading_accuracy = 40
        if short_passing == None:
            short_passing = 40
        if volleys == None:
            volleys = 40
        if dribbling == None:
            dribbling = 40
        if curve == None:
            curve = 40
        if free_kick_accuracy == None:
            free_kick_accuracy = 40
        if long_passing == None:
            long_passing = 40
        if ball_control == None:
            ball_control = 40
        if long_shots == None:
            long_shots = 40
        if penalties == None:
            penalties = 40
        if attacking_work_rate == None:
            attacking_work_rate = 40
        if crossing == None:
            crossing = 40
        if finishing == None:
            finishing = 40
        if shot_power == None:
            shot_power = 40
        if defensive_work_rate == None:
            defensive_work_rate = 40
        if standing_tackle == None:
            standing_tackle = 40
        if marking == None:
            marking = 40
        if interceptions == None:
            interceptions = 40
        if gk_diving == None:
            gk_diving = 4
        if gk_handling == None:
            gk_handling = 4
        if gk_kicking == None:
            gk_kicking = 4
        if gk_positioning == None:
            gk_positioning = 4
        if gk_reflexes == None:
            gk_reflexes = 4
        if overall_rating == None:
            overall_rating = 50

        attacking = (attacking_work_rate + crossing + finishing + shot_power) / 4
        defensive = (defensive_work_rate + standing_tackle + sliding_tackle + marking + interceptions) / 5
        physical = (acceleration + sprint_speed + agility + balance + jumping + stamina + strength) / 7
        mental = (reactions + aggression + positioning + interceptions + vision) / 5
        technical = (
                        potential + heading_accuracy + short_passing + volleys + dribbling + curve + free_kick_accuracy + long_passing + ball_control + long_shots + penalties) / 11
        goalkeeping = (gk_diving + gk_handling + gk_kicking + gk_positioning + gk_reflexes) / 5

        one_guy_attr = [attacking, defensive, physical, mental, technical, goalkeeping]

        attr_list.append(one_guy_attr)
        complete_attr_list.append([attacking, defensive, physical, mental, technical, goalkeeping, player_id, overall_rating])

    pca = PCA(n_components=2)
    results = pca.fit_transform(np.array(attr_list))

    for i in range(0, len(results)):
        complete_attr_list[i].append(results[i][0])
        complete_attr_list[i].append(results[i][1])

    minX = sys.maxint
    maxX = 0
    minY = sys.maxint
    maxY = 0

    for player in complete_attr_list:
        player_id = player[6]
        player_x = player[8]
        player_y = player[9]
        if(player_x < minX):
            minX = player_x
        if(player_x > maxX):
            maxX = player_x
        if(player_y < minY):
            minY = player_y
        if(player_y > maxY):
            maxY = player_y
        name, height, weight = getPlayerNameHeightWeight(player_id)
        player.append(name)
        player.append(height)
        player.append(weight)

    # for player in complete_attr_list:
    #     player_id = player[6]
    #     pos = getPlayerPosition(player_id)
    #     player.append(pos)

    final_player_dict = {}
    for player in complete_attr_list:
        attributes_names_list = ['Att', 'Def', 'Phy', 'Men', 'Tech', 'GK', 'id', 'Ovl', 'X', 'Y', 'Name', 'Ht', 'Wt']
        dict_list = zip(attributes_names_list, player)
        dict_list = dict(dict_list)
        player_id = player[6]
        final_player_dict[player_id] = dict_list

    final_dict = {}
    final_dict['minX'] = minX
    final_dict['minY'] = minY
    final_dict['maxY'] = maxX
    final_dict['maxY'] = maxY
    final_dict['player_list'] = final_player_dict

    # print final_dict

    return final_dict



# getPlayerAttributes()
# getPlayerPosition("111")

# season = "2015/2016"
# getEndSeasonStatisticsOfTeamForSeason("1729", season, "8668")
#
# for i in range(0, 7):
#     halves = season.split("/")
#     first_half = halves[0]
#     second_half = halves[1]
#     first_half = int(first_half) - 1
#     second_half = int(second_half) - 1
#     season = str(first_half) + "/" + str(second_half)
#     getEndSeasonStatisticsOfTeamForSeason("1729", season, "8668")


# getHistoryStatsForTeam("1729", "2008/2009", "8668")

# getSeasonwideStandingsDetails("1729", "2015/2016")
# names = getTeamLongAndShortNames("9985")
# print names

# print gameweek_result

# result = getStandingsDetailsForGameweek("1729", "2014/2015", 2)
#
# sorted_result = sorted(result.items(), key=lambda k: (k[1][1], k[1][7]), reverse=True)
# all_position = []
# for club in sorted_result:
#     all_position.append(club[0])
#
# for key, value in result.iteritems():
#     # Add position to each club
#     pos = all_position.index(key)
#     value[0] = pos + 1
#
#     team_id = value[4]
#     oppn_id = value[5]
#     team_names = getTeamLongAndShortNames(team_id)
#     oppn_names = getTeamLongAndShortNames(oppn_id)
#
#     value[7] = str(team_names[0])
#     value[8] = str(team_names[1])
#     value[9] = str(oppn_names[0])
#     value[10] = str(oppn_names[1])
#
# attributes_names_list = ['pos', 'points', 'GD', 'match_id', 'team_id', 'oppn_id', 'score', 'team_short_name',
#                          'team_long_name', 'oppn_short_name', 'oppn_long_name']
# for key, value in result.iteritems():
#     dict_list = zip(attributes_names_list, value)
#     dict_list = dict(dict_list)
#     gameweek_result.append(dict_list)
