# nba-regression
NBA Matchup Prediction Model Using Logistic Regression

[@BasketBrainBot](https://twitter.com/BasketBrainBot) on twitter tweets out game picks each day! Bot is deployed using Google Cloud Functions.

## Running Predictions
To get predictions for NBA matchups locally, run the following commands in the project directory.

1. Install dependencies


```pip install -r requirements.txt```

2. Get predictions for todays matchups

```python main.py```

3. Get predictions for a historic date

```python main.py <MM/DD/YYYY>```


## Data
All data is webscraped using BeautifulSoup [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) from [TeamRankings.com](https://www.teamrankings.com/) and [Basketball-Reference.com](https://www.basketball-reference.com). The ```scraper.py``` file can scrape NBA matchup data from a range of dates and export as a CSV. 

It also has the ability to retrieve matchup data for the current days games and return in a format to be used with pandas.

There are various .csv files under the `data/` directory containing training data for the model.

## Training
Model is created and trained using the scikit-learn's Logistic Regression library. Jupyter notebook containing the training steps can be found at ```regression_model.ipynb```

## Model Performance 
Training the model on the entire 2022/23 NBA season (1280 matchups), I was able to acheive an accuracy that varies from 0.57 - 0.68.

The AUC-ROC score was 0.62 - 0.68.

Further analysis and visualizations in the ```regression_model.ipynb``` file.

## Setting Up Twitter Bot
If you wish to set up your own prediction Twitter bot on the Google Cloud Platform you can use the contents under the ```bot/``` directory.

Make sure to copy the ```bot/.env.template``` as ```bot/.env``` and fill out the credentials for the Twitter API and GCP.

The ```bot/gcp_main.py``` file is set up to work with a google cloud function configured with a pub/sub trigger. You need to upload the .sav file with the model weights to a bucket to be downloaded at runtime due to storage limits. 

