# nba-regression
NBA Matchup Prediction Model Using Logistic Regression

[@BasketBrainBot](https://twitter.com/BasketBrainBot) on twitter tweets out game picks each day! Bot is deployed using Google Cloud Functions.

## Data
All data is webscraped using BeautifulSoup [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) from [TeamRankings.com](https://www.teamrankings.com/) and [Basketball-Reference.com](https://www.basketball-reference.com). The `scraper.

There are various .csv files under the `data/` directory containing training data for the model.

## Model Performance 
Training the model on the entire 2022/23 NBA season (1280 matchups), I was able to acheive an accuracy that varies from 0.57 - 0.68.

The AUC-ROC score was 0.62 - 0.68



