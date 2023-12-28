from datetime import datetime, timedelta
from bs4 import BeautifulSoup
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
        if len(games) == 0:
            print(f'No matchups on {self.date}')
            return None 
        print(f'{len(games)} matches found')

        converted_team_names = [self._name_dict.get(team, "Invalid team") for team in teams]
        team_stats = self._get_team_stats(converted_team_names)
        if team_stats is None:
            print("Error: No team stats found")
            return None

        for matchup in games:
            home_team = matchup[0]
            away_team = matchup[1]
            outcome = matchup[2]
            game_date = matchup[3]
            home_stats = team_stats[self._name_dict[home_team]]
            away_stats = team_stats[self._name_dict[away_team]]
            
            obj = {'home_team': home_team, 'away_team': away_team, 'date': game_date}
            if outcome != None: obj['outcome'] = int(outcome)
            for stat in self.stats:
                home_stat = f'home_{stat}'
                away_stat = f'away_{stat}'
                obj[home_stat] = home_stats[stat]
                obj[away_stat] = away_stats[stat]

            data.append(obj)
        return data


    # Downloads csv of matchups over a time period or between seasons
    # Params: start_date/end_date -> 'month/day/year' 2 digits for month/day 4 digits for year!!
    def get_matchups_over_period(self, start_date, end_date):
        MAX_YEARS = 5
        output = []
        total_days = self._find_number_of_days(start_date, end_date)

        self.date, i = start_date, 0
        
        while i < total_days:
            if i > (MAX_YEARS * 365):
                print("Error: Max years exceeded")
                return None
            
            data = self.get_todays_matchups()
            self._update_date()
            output.append(data)
            i += 1
            print(f'{i/total_days * 100:.2f}% complete')

        return output


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

                    outcome = None
                    home_pts = row.find('td', attrs={'data-stat': 'home_pts'})
                    away_pts = row.find('td', attrs={'data-stat': 'visitor_pts'})

                    if home_pts.get_text() != '' and away_pts.get_text() != '':
                        outcome = 1 if int(home_pts.get_text()) > int(away_pts.get_text()) else 0
                    
                    games.append((home_team, away_team, outcome, game_date))
        
        return games, teams


    # Return curent stats of all teams in teams list
    def _get_team_stats(self, teams):
        data, delay = {}, 20
        for stat in self.stats:
            tr_url = self._get_stats_url(stat)
            response = requests.get(tr_url)

            while response.status_code != 200:
                print(f"Error: {response.status_code} status code at url: {tr_url}, delaying {delay} seconds...")
                time.sleep(delay)
                response = requests.get(tr_url)
                delay += 5

            html_content = response.text
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
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 
            10: "October", 11: "November", 12: "December"
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

    # Increment date by one day
    def _update_date(self):
        parts = self.date.split('/')
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])

        # Get the last day of the current month
        last_day = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day

        # Check if it's the last day of the month
        if day == last_day:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            day = 1
        else:
            day += 1

        self.date = f"{month:02d}/{day:02d}/{year}"


    def _find_number_of_days(self, start_date, end_date):
        start = datetime.strptime(start_date, '%m/%d/%Y')
        end = datetime.strptime(end_date, '%m/%d/%Y')
        return abs((end - start).days)
            
    def write_to_csv(self, data):
        filename = f'matchups.csv'
        id = 0
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            header = ['id', 'date', 'home_team', 'away_team', 'outcome']
            for stat in self.stats: 
                header.append(f'home_{stat}')
                header.append(f'away_{stat}')
            writer.writerow(header)  # Write header row

            for day in data:
                for matchup in day:
                    row = [id, matchup['date'], matchup['home_team'], matchup['away_team'], matchup['outcome']]
                    for stat in self.stats: 
                        row.append(matchup[f'home_{stat}'])
                        row.append(matchup[f'away_{stat}'])
                    writer.writerow(row)
                    id += 1

        print(f"CSV file '{filename}' created successfully.")

if __name__ == "__main__":
    scraper = Scraper()
    out = scraper.get_matchups_over_period('10/20/2022', '4/02/2023')
    scraper.write_to_csv(out)
    
