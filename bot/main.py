import pandas as pd
from scraper import Scraper
from joblib import load
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

MODEL_PATH = 'bot/finalized_model.sav'

def main():
    scraper = Scraper()

    data = scraper.get_todays_matchups()
    df = pd.DataFrame(data)

    X = df.drop(['date', 'home_team', 'away_team'], axis=1)

    # Normalize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Load the model
    model = load(MODEL_PATH)
    
    predictions = model.predict_proba(X_scaled)
    print(df.loc[0])
    
    for i in range(len(data)):
        print(f'Home Team: {data[i]["home_team"]}, Away Team: {data[i]["away_team"]}')

        winner, prob = data[i]['home_team'] if predictions[i][1] > predictions[i][0] else data[i]['away_team'], max(predictions[i])
        prob_percentage = prob * 100
        print(f'Projected Winner: {winner}')
        print(f'Probability: {prob_percentage:.1f}%')


if __name__ == "__main__":
    main()