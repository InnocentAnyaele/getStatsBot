import requests
import json

LEAGUES = {
    'english-premier-league': 39,
    'epl': 39,
    'premier-league': 39,
    'premier': 39,
    'la-liga': 140,
    'laliga': 140,
    'laligasantander': 140,
    'laliga-santander': 140,
    'la-liga-santander': 140,
    'bundesliga': 78,
    'bundesliga1': 78,
    'budesliga-1': 78,
    'ucl': 2,
    'uefa-champions-league': 2,
    'champions-league': 2,
    'champions': 2,
    'seriaa': 135,
    'searia-a': 135,
    'ligue1': 61,
    'ligue-1': 61,
    'fa-cup': 45,
    'facup': 45,
    'efl' : 45,
    'europa': 3,
    'uefa-europa': 3,
    'europa-league': 3,
    'uefa-europa-league': 3,
    'europa-conference': 848,
    'europa-conference-league': 848,
    'uefa-europa-conference-league': 848,
    'afcon': 6,
    'africa-cup-of-nations': 6,
    'carabao': 46,
    'carabao-cup': 46,
    'super-cup': 556,
    'super-copa': 556,
    'supercup': 556,
    'supercopa': 556,
    'euros': 4,
    'euro-championship': 4,
    'world-cup': 1,
    'worldcup': 1,
    'copa-del-ray': 143,
    'copadelray': 143,
    'club-world-cup': 15,
    'clud-worldcup': 15,
    'fifa-club-worldcup': 15,
    'fifa-club-world-cup': 15,
}


def getAllLeagues():
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"

    headers = {
        "X-RapidAPI-Key": "2202bb1fd1mshe308a9467ccd12ep1732fajsn60bb4bb4d35e",
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers)
        league_data = json.loads(response.text)
        league_data_response = league_data['response']
        response_headers = response.headers
        print(league_data_response)
        print(response_headers)
    except Exception as e:
        print(Exception)


def getLeagueID(league):
    try:
        return LEAGUES[str(league)]
    except:
        return None


