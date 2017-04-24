from flask import Flask
from flask import render_template
from flask import request
import json

import database_manager

app = Flask(__name__)

latest_season = "2015/2016"


@app.route("/data/epl/teams/standings")
def getSeasonStandings():
    season_details = database_manager.getStandingsOfTeamForSeason("1729", "2014/2015")
    standings_dict = {}
    for detail in season_details:
        standings_dict[detail] = season_details[detail][0]
    standings_json = json.dumps(standings_dict)
    print standings_json
    return standings_json


@app.route("/data/countries/")
def getAllCountries():
    countries_shown = database_manager.getAllCountries()
    list_dict_countries = []
    for country_detail in countries_shown:
        dict_country = {}
        dict_country['country_id'] = country_detail[0]
        dict_country['country_name'] = country_detail[1]
        list_dict_countries.append(dict_country)
    json_countries = json.dumps(list_dict_countries)
    # print json_countries
    return json_countries


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


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
