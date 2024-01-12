import os
import tweepy
import pandas as pd
from joblib import load
from dotenv import load_dotenv
from scraper import Scraper
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

MODEL_PATH = 'bot/finalized_model.sav'

load_dotenv()
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
CONSUMER_KEY = os.getenv('TWITTER_API_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_API_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

def main():
    scraper = Scraper()

    data = scraper.get_todays_matchups()
    tweets = get_predictions(data)

    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    for prediction in tweets:
        response = client.create_tweet(text=prediction)
        print(prediction)


def get_predictions(data):
    df = pd.DataFrame(data)

    X = df.drop(['date', 'home_team', 'away_team'], axis=1)

    # Normalize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Load the model
    model = load(MODEL_PATH)
    
    predictions = model.predict_proba(X_scaled)
    tweets = []
    
    for i in range(len(data)):
        away, home = data[i]["away_team"], data[i]["home_team"]
        out = f'{away} {get_team_emoji(away)}  @  {home} {get_team_emoji(home)}\n\n'

        winner, prob = home if predictions[i][1] > predictions[i][0] else away, max(predictions[i])
        prob_percentage = prob * 100
        out += f'Projected Winner: {winner} {get_team_emoji(winner)}\nProbability: {prob_percentage:.1f}%'

        tweets.append(out)

    return tweets


def get_team_emoji(teamname):
    emoji_map = {
        "Atlanta Hawks": '🦅', "Boston Celtics": '🍀', "Brooklyn Nets": '🏙️', "Charlotte Hornets": '🐝', "Chicago Bulls": '🐂', "Cleveland Cavaliers": '⚔️', "Dallas Mavericks": '🐴',
        "Denver Nuggets": '⛏️', "Detroit Pistons": '🚗', "Golden State Warriors": '🌉', "Houston Rockets": '🚀', "Indiana Pacers": '🏎️', "Los Angeles Clippers": '✂️', "Los Angeles Lakers": '🏀', "Memphis Grizzlies": '🐻', 
        "Miami Heat": '🔥', "Milwaukee Bucks": '🦌', "Minnesota Timberwolves": '🐺', "New Orleans Pelicans": '🐦', "New York Knicks": '🗽', "Oklahoma City Thunder": '⚡',
        "Orlando Magic": '🪄', "Philadelphia 76ers": '🔔', "Phoenix Suns": '☀️', "Portland Trail Blazers": '🌲', "Sacramento Kings": '👑', "San Antonio Spurs": '🤠',"Toronto Raptors": '🦖', "Utah Jazz": '🎷', "Washington Wizards": '🧙‍♂️',
    }

    return emoji_map[teamname]


if __name__ == "__main__":
    main()