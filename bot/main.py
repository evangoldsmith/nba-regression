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
        print(response)


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
        out = f'{data[i]["away_team"]} @ {data[i]["home_team"]}\n\n'

        winner, prob = data[i]['home_team'] if predictions[i][1] > predictions[i][0] else data[i]['away_team'], max(predictions[i])
        prob_percentage = prob * 100
        out += f'Projected Winner: {winner}\nProbability: {prob_percentage:.1f}%'

        tweets.append(out)

    return tweets



if __name__ == "__main__":
    main()