from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import csv
import time

class Scraper():

    def __init__(self, date=None):

        # dict to map team names between basketball-reference and teamrankings in url patterns
        self._name_dict = {
            "Atlanta Hawks": 'Atlanta', "Boston Celtics": 'Boston', "Brooklyn Nets": 'Brooklyn', "Charlotte Hornets": 'Charlotte', "Chicago Bulls": 'Chicago', "Cleveland Cavaliers": 'Cleveland', "Dallas Mavericks": 'Dallas',
            "Denver Nuggets": 'Denver', "Detroit Pistons": 'Detroit', "Golden State Warriors": 'Golden State', "Houston Rockets": 'Houston', "Indiana Pacers": 'Indiana', "Los Angeles Clippers": 'LA Clippers', "Los Angeles Lakers": 'LA Lakers', "Memphis Grizzlies": 'Memphis', 
            "Miami Heat": 'Miami', "Milwaukee Bucks": 'Milwaukee', "Minnesota Timberwolves": 'Minnesota', "New Orleans Pelicans": 'New Orleans', "New York Knicks": 'New York', "Oklahoma City Thunder": 'Okla City',
            "Orlando Magic": 'Orlando', "Philadelphia 76ers": 'Philadelphia', "Phoenix Suns": 'Phoenix', "Portland Trail Blazers": 'Portland', "Sacramento Kings": 'Sacramento', "San Antonio Spurs": 'San Antonio',"Toronto Raptors": 'Toronto', "Utah Jazz": 'Utah', "Washington Wizards": 'Washington',
        }

        self.stats = ['points-per-game', 'true-shooting-percentage', 'offensive-rebounds-per-game', 'defensive-rebounds-per-game', 'steals-per-game', 'assist--per--turnover-ratio', 'personal-fouls-per-game', 'win-pct-all-games']
        self.teams = ['Atlanta', 'Boston', 'Brooklyn', 'Charlotte', 'Chicago', 'Cleveland', 'Dallas', 'Denver', 'Detroit', 'Golden State', 'Houston', 'Indiana', 'LA Clippers', 'LA Lakers', 'Memphis', 'Miami', 'Milwaukee', 'Minnesota', 'New Orleans', 'New York', 'Okla City', 'Orlando', 'Philadelphia', 'Phoenix', 'Portland', 'Sacramento', 'San Antonio', 'Toronto', 'Utah', 'Washington']
        self.date = time.strftime("%m/%d/%Y") if not date else date



    # Return matchups for current date, with current team stats
    def get_todays_matchups(self):
        data = []
        print(f"Getting matchups for {self.date}...")

        games, teams = self._get_games()
        print(f'{len(games)} matches with {len(teams)} teams playing')
        converted_team_names = [self._name_dict.get(team, "Invalid team") for team in teams]
        team_stats = self._get_team_stats(converted_team_names)

        for matchup in games:
            home_team = matchup[0]
            away_team = matchup[1]
            home_stats = team_stats[self._name_dict[home_team]]
            away_stats = team_stats[self._name_dict[away_team]]
            
            obj = {'home_team': home_team, 'away_team': away_team}
            for stat in self.stats:
                home_stat = f'home_{stat}'
                away_stat = f'away_{stat}'
                obj[home_stat] = home_stats[stat]
                obj[away_stat] = away_stats[stat]
            
            data.append(obj)
        return data
    

    # Return list of games, and list of teams playing
    def _get_games(self):
        br_url = self._get_schedule_url()
        if br_url is None:
            return None
        
        response = requests.get(br_url) 
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')

        games, teams = [], []
        for row in rows:
            date_element = row.find('a')
            if date_element:
                game_date = self._format_date(date_element.get_text())

                if game_date == self.date:
                    home_team = row.find('td', attrs={'data-stat': 'home_team_name'}).get_text()
                    away_team = row.find('td', attrs={'data-stat': 'visitor_team_name'}).get_text()
                    teams.extend([home_team, away_team])
                    games.append((home_team, away_team))
        
        return games, teams


    # Return curent stats of all teams in teams list
    def _get_team_stats(self, teams):
        data = {}
        for stat in self.stats:
            tr_url = self._get_stats_url(stat)
            response = requests.get(tr_url)
            html_content = response.text

            if response.status_code != 200:
                print(f"Error: {response.status_code} response from {tr_url}")
                return None

            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table')
            if not table:
                print(f"Error: No table found for stat at url: {tr_url}")
                return None
            rows = table.find_all('tr')

            for row in rows:
                v = row.find('td', class_='text-right')
                team_element = row.find('a')
                if team_element and v and team_element.get_text() in teams:

                    team_name, value = team_element.get_text(), v.get_text()
                    if '%' in value:
                        value = value[:-1]

                    if team_name not in data:
                        data[team_name] = {stat: value}
                    else:
                        data[team_name][stat] = value

        if not data:
            print("Error: No team statistics found")
            return None

        return data


    def _get_stats_url(self, stat):
        parts = self.date.split('/')
        month, day, year = parts[0], parts[1], parts[2]
        
        return f"https://www.teamrankings.com/nba/stat/{stat}?date={year}-{month}-{day}"
    

    def _get_schedule_url(self):
        parts = self.date.split('/')
        year, month = int(parts[2]), int(parts[0])
        months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }
        
        if month not in months:
            print("Invalid month")
            return None

        if month > 4:
            year += 1
        
        m = months.get(month, "Invalid month")
        return f'https://www.basketball-reference.com/leagues/NBA_{str(year)}_games-{m.lower()}.html'

    def _format_date(self, date_string):
        datetime_obj = datetime.strptime(date_string, '%a, %b %d, %Y')
        formatted_date = datetime_obj.strftime('%m/%d/%Y')
        return formatted_date
        

if __name__ == "__main__":
    scraper = Scraper()
    data = scraper.get_todays_matchups()

    df = pd.DataFrame(data)
    print(df)
