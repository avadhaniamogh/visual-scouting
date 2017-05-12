from flask import Flask
from flask import render_template
from flask import request
import json

import database_manager

app = Flask(__name__)

latest_season = "2015/2016"

'''
================================================
NOTE: In all the places country_id = league_id
================================================
'''


# - (1)
@app.route("/data/stats/")
def getEndSeasonStatistics():
    country_id = request.args.get('country_id')
    season_details = database_manager.getEndSeasonStatisticsOfTeamsForSeason(country_id, latest_season)
    return season_details


# - (2)
@app.route("/data/standings/")
def getWeekByWeekStandings():
    country_id = request.args.get('country_id')
    week_by_week_details = database_manager.getSeasonwideStandingsDetails(country_id, latest_season)
    return week_by_week_details


@app.route("/data/menu/")
def getMenu():
    countries_shown = database_manager.getAllCountries()
    list_dict_countries = []
    for country_detail in countries_shown:
        dict_country = {}
        dict_country['country_id'] = country_detail[0]
        dict_country['country_name'] = country_detail[1]
        country_id = country_detail[0]
        teams = database_manager.getTeamsForSeason(country_id, latest_season)
        list_dict_teams = []
        for team in teams:
            dict_team = {}
            dict_team['team_id'] = team[0]
            dict_team['long_name'] = team[1]
            dict_team['short_name'] = team[2]
            list_dict_teams.append(dict_team)

        dict_country['teams'] = list_dict_teams
        list_dict_countries.append(dict_country)
    json_countries = json.dumps(list_dict_countries)
    print json_countries
    return json_countries

    # list_dict_countries = []
    # for country_detail in countries_shown:
    #     dict_country = {}
    #     dict_country['country_id'] = country_detail[0]
    #     dict_country['country_name'] = country_detail[1]
    #     list_dict_countries.append(dict_country)
    # json_countries = json.dumps(list_dict_countries)
    # # print json_countries
    # return json_countries


@app.route("/data/countries/teams")
def getTeamsFromCountry():
    country_id = request.args.get('country_id')
    teams = database_manager.getTeamsForSeason(country_id, latest_season)
    # print teams
    list_dict_teams = []
    for team in teams:
        dict_team = {}
        dict_team['team_id'] = team[0]
        dict_team['long_name'] = str(team[1])
        dict_team['short_name'] = str(team[2])
        list_dict_teams.append(dict_team)
    json_teams = json.dumps(list_dict_teams)
    print json_teams
    return json_teams


@app.route("/data/teams/history")
def getHistoryStandingsForTeam():
    team_id = request.args.get('team_id')
    league_id = request.args.get('country_id')
    season = latest_season
    team_stats = database_manager.getEndSeasonStatisticsOfTeamForSeason(league_id, season, team_id)
    data = {}
    data[season] = team_stats

    for i in range(0, 7):
        halves = season.split("/")
        first_half = halves[0]
        second_half = halves[1]
        first_half = int(first_half) - 1
        second_half = int(second_half) - 1
        season = str(first_half) + "/" + str(second_half)
        database_manager.getEndSeasonStatisticsOfTeamForSeason(league_id, season, team_id)
        data[season] = team_stats


    json_data = json.dumps(data)

    print json_data
    return json_data

@app.route("/data/global/scout")
def getAllPlayerAttributes():
    player_attributes = database_manager.getPlayerAttributes()
    json_data = json.dumps(player_attributes)

    print json_data

    return json_data

@app.route("/data/global/scout/filter")
def getAllPlayerAttributesWithFilter():
    min_ovl = request.args.get('min_ovl')
    max_ovl = request.args.get('max_ovl')
    player_attributes = database_manager.getPlayerAttributesWithFiler(min_ovl, max_ovl)
    json_data = json.dumps(player_attributes)

    print json_data

    return json_data

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
