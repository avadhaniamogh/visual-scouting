import sqlite3

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()


def getAllCountries():
    query = "Select * from Country"
    cursor.execute(query)
    countries = []
    for row in cursor:
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
    teams_query = "Select * from Team where team_api_id = ?"
    for team_id in team_ids:
        cursor.execute(teams_query, (team_id,))
        for row in cursor:
            teams.append(row)
    return teams


# Returned dictionary is of the form <TeamId, [Points, Wins, Draws, Losses, GF, GA, GD]>
def getStandingsOfTeamForSeason(league_id, season):
    get_standings_query = "Select home_team_goal, away_team_goal, home_team_api_id, away_team_api_id From Match Where season = ? And league_id = ?;";
    all_standings = {}
    cursor.execute(get_standings_query, (season, league_id,))
    for row in cursor:
        homeTeamGoal = row[0]
        awayTeamGoal = row[1]
        homeTeamId = row[2]
        awayTeamId = row[3]

        if homeTeamId not in all_standings:
            all_standings[homeTeamId] = [0] * 7
        if awayTeamId not in all_standings:
            all_standings[awayTeamId] = [0] * 7

        home_team_result_list = all_standings[homeTeamId]
        away_team_result_list = all_standings[awayTeamId]

        if int(homeTeamGoal) > int(awayTeamGoal):
            home_team_result_list[1] += 1  # win for home team
            home_team_result_list[0] += 3  # 3 points for home team
            away_team_result_list[3] += 1  # loss for away team
        elif int(awayTeamGoal) > int(homeTeamGoal):
            home_team_result_list[2] += 1  # draw for home team
            home_team_result_list[0] += 1  # 1 point for home team

            away_team_result_list[2] += 1  # draw for away team
            away_team_result_list[0] += 1  # 1 point for away team
        else:
            home_team_result_list[3] += 1  # loss for home team

            away_team_result_list[1] += 1  # win for away team
            away_team_result_list[0] += 3  # 3 points for away win

            home_team_result_list[4] += int(homeTeamGoal)  # GF
            home_team_result_list[5] += int(awayTeamGoal)  # GA
            home_team_result_list[6] += (int(homeTeamGoal) - int(awayTeamGoal))

        away_team_result_list[4] += int(awayTeamGoal)  # GF
        away_team_result_list[5] += int(homeTeamGoal)  # GA
        away_team_result_list[6] += int(awayTeamGoal) - int(homeTeamGoal)

        all_standings[homeTeamId] = home_team_result_list
        all_standings[awayTeamId] = away_team_result_list

    return all_standings


# teams = getTeamsForSeason("1729", "2014/2015")
# print teams

# getStandingsOfTeamForSeason("1729", "2014/2015")
