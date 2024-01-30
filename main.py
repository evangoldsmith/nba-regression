import sys
import pandas as pd
import csv
from joblib import load
from scraper import Scraper
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

MODEL_PATH = 'finalized_model.sav'
CSV_PATH = 'records.csv'

def main():

    historic = False

    # Check if date was passed in
    if len(sys.argv) > 1:
        date_arg = sys.argv[1]
        historic = True

    # Change date by passing in 'date' argument -> Scraper(date='MM/DD/YYYY')
    scraper = Scraper() if not historic else Scraper(date=date_arg)

    data = scraper.get_todays_matchups()
    write_predictions(data, historic)
    predictions = get_predictions(data, historic)

    for prediction in predictions:
        print('\n------------\n')
        print(prediction)
    print('\n------------\n')


def get_predictions(data, historic):
    df = pd.DataFrame(data)        
    X = df.drop(['date', 'home_team', 'away_team'], axis=1) if not historic else df.drop(['date', 'home_team', 'away_team', 'outcome'], axis=1)

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


def write_to_csv(self, data):
    filename, id = f'matchups.csv', 0

    with open(CSV_PATH, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['id', 'date', 'home_team', 'away_team', 'outcome', 'prediction']

        for stat in self.stats: 
            header.append(f'home_{stat}')
            header.append(f'away_{stat}')

        writer.writerow(header)  # Write header row

        for day in data:
            if day is None:
                continue
            for matchup in day:
                row = [id, matchup['date'], matchup['home_team'], matchup['away_team'], matchup['outcome']]
                for stat in self.stats: 
                    row.append(matchup[f'home_{stat}'])
                    row.append(matchup[f'away_{stat}'])
                writer.writerow(row)
                id += 1

    print(f"CSV file '{filename}' created successfully.")


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