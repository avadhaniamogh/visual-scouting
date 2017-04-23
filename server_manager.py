from flask import Flask
from flask import render_template
import json

import database_manager

app = Flask(__name__)

@app.route("/data/epl/teams/standings")
def getSeasonStandings():
    season_details = database_manager.getStandingsOfTeamForSeason("1729", "2014/2015")
    standings_dict = {}
    for detail in season_details:
        standings_dict[detail] = season_details[detail][0]
    standings_json = json.dumps(standings_dict)
    print standings_json
    return standings_json

@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
