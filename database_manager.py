import sqlite3
import json
import collections
import unicodedata

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


getHistoryStatsForTeam("1729", "2008/2009", "8668")

# result = getPlayersForTeamInSeason("2015/2016")
# print result

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
