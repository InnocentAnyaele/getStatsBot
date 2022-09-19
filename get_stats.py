import tweepy
# import keys
import requests
import datetime
import json
import time
import leagues
import os
from dotenv import load_dotenv

load_dotenv()

CONSUMER_API_KEY = os.getenv('CONSUMER_API_KEY')
CONSUMER_API_KEY_SECRET = os.getenv('CONSUMER_API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
ACCESS_TOKEN2 = os.getenv('ACCESS_TOKEN2')
ACCESS_TOKEN_SECRET2 = os.getenv('ACCESS_TOKEN_SECRET2')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
STATS_KEY_API = os.getenv('STATS_API_KEY')


def getAuthForDeveloperAccount():
    dev_auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_KEY_SECRET)
    dev_auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    dev_api = tweepy.API(dev_auth, wait_on_rate_limit=True)
    return dev_api


def getAuthForBot():
    bot_client = tweepy.Client(BEARER_TOKEN, CONSUMER_API_KEY, CONSUMER_API_KEY_SECRET,
                               ACCESS_TOKEN2, ACCESS_TOKEN_SECRET2)
    bot_auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_KEY_SECRET)
    bot_auth.set_access_token(ACCESS_TOKEN2, ACCESS_TOKEN_SECRET2)
    bot_api = tweepy.API(bot_auth, wait_on_rate_limit=True)
    return (bot_client, bot_auth, bot_api)


def getAccessTokenForBotAccount():
    auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_KEY_SECRET, callback='oob')
    auth.secure = True
    auth_url = auth.get_authorization_url()
    print('Please authorize: ' + auth_url)

    verifier = input('PIN: ').strip()
    print(verifier)

    auth.get_access_token(verifier)

    print(auth.access_token)
    print(auth.access_token_secret)
    return auth


def verifyBotCredentials(bot_api):
    try:
        bot_api.verify_credentials()
    except:
        print('something went wrong')


def getLastID():
    f = open('tweet_ID.txt', 'r')
    lastId = int(f.read().strip())
    return lastId


def putLastID(Id):
    f = open('tweet_ID.txt', 'w')
    f.write(str(Id))
    f.close()
    return


def findLeagueAndSeason(text):
    current_season = datetime.date.today().year
    print(current_season)
    text_array = text.split(' ')
    league = ''
    season = ''
    print(text_array)
    playerName = ''
    for i in range(len(text_array)):
        if text_array[i].lower() == '@getstatsbot':
            text_array = text_array[i + 1:]
            break
    if len(text_array) < 1:
        return None, None
    if len(text_array) == 1:
        return text_array[0], current_season
    else:
        return text_array[0], text_array[1]


def getStatsFromApi(league, season):
    league_id = leagues.getLeagueID(league)
    import requests

    url = "https://api-football-v1.p.rapidapi.com/v3/players/topscorers"

    querystring = {"league": league_id, "season": season}

    headers = {
        "X-RapidAPI-Key": STATS_KEY_API,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
    except Exception as e:
        print(e)

    response_limit = response.headers['X-RateLimit-requests-Limit']
    response_remaining = response.headers['X-RateLimit-requests-Remaining']
    response_status = response.status_code
    response_data = json.loads(response.text)
    response_header = response.headers

    result_length = response_data['results']

    if result_length > 0:
        results = response_data['response']
        reply_text = f"Thank you for using getStatsBot. \n \n {league} {season} top 5 scorers \n Goals - Assists - Penalties \n \n"
        # stats = []
        for i in range(5):
            name = results[i]['player']['name']
            goals = results[i]['statistics'][0]['goals']['total']
            assists = results[i]['statistics'][0]['goals']['assists']
            penalties = results[i]['statistics'][0]['penalty']['scored']
            reply_text += f"{i + 1}. {name} - {goals} - {assists} - {penalties}\n"
            statusFound = True

    else:
        statusFound = None

    if statusFound is None:
        reply_text = "Your request could not be completed. \n Format should be: \n [getStatsBot league] to get the current top scorers of the season \n [getStatsBot league season] for a specific season."

    # print(statusFound)
    # print(response_data)
    return reply_text


def send_reply(tweet_text, tweet_id):
    failed_reply_text = "{} Your request could not be completed. \n Format should be: \n [getStatsBot league] to get the current top scorers of the season \n [getStatsBot league season] for a specific season."
    try:
        league, season = findLeagueAndSeason(tweet_text)
        if league is None:
            # print('reached here')
            # print('this means the problem is with the stream')
            print(failed_reply_text)
            bot_api.update_status(
                failed_reply_text,
                in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
            putLastID(tweet_id)
        else:
            reply_text = getStatsFromApi(league, season)
            print(reply_text)
            bot_api.update_status(status=reply_text,
                                  in_reply_to_status_id=tweet_id, auto_populate_reply_metadata=True)
            putLastID(tweet_id)
    except Exception as e:
        print(e)


class CustomStreamListener(tweepy.StreamingClient):

    def on_tweet(self, tweet):
        print('new tweet intake')
        tweet_id = tweet.id
        tweet_text = tweet.text
        tweet_text = tweet_text.lower()
        lastId = getLastID()
        mentioned_tweet = tweet_text.find("@getstatsbot")
        if mentioned_tweet > -1:
            send_reply(tweet_text, tweet_id)
        time.sleep(5)

    def on_connect(self):
        print("Connected and listening")

    def on_errors(self, status_code):
        self.disconnect()
        if status_code == 420:
            # returning False in on_data disconnects the stream
            self.disconnect()
            return False


def respondToTweet():
    last_id = getLastID()
    # print(last_id)
    mentions = bot_api.mentions_timeline(since_id=last_id)
    if len(mentions) == 0:
        print('None found')
        time.sleep(10)
        return
    new_id = 0
    for mention in reversed(mentions):
        print('-----------------------------')
        print(mention)
        author = mention.author.screen_name
        new_id = mention.id
        tweet_id = mention.id
        tweet_text = mention.text.lower()
        print(tweet_id)
        print(tweet_text)
        mentioned_tweet = tweet_text.find("@getstatsbot")
        print(mentioned_tweet)
        if mentioned_tweet > -1:
            print('yes, it includes it')
            send_reply(tweet_text, tweet_id)
        time.sleep(5)
    putLastID(new_id)


def start_stream():
    while True:
        stream = CustomStreamListener(BEARER_TOKEN, wait_on_rate_limit=True)
        previousRules = stream.get_rules().data
        stream.delete_rules(previousRules)
        print(previousRules)
        rule = tweepy.StreamRule(value="@getStatsBot")
        stream.add_rules(rule)
        stream.filter(tweet_fields=["id", "text"])


def start_response():
    while True:
        respondToTweet()


bot_client, bot_auth, bot_api = getAuthForBot()

if __name__ == "__main__":
    start_stream()
    # start_response()
