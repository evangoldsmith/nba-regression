from bs4 import BeautifulSoup
import requests
import csv
import time
from datetime import datetime

# November - https://www.basketball-reference.com/leagues/NBA_2023_games-november.html
# Home team, away team, win/loss (home team), home team stats, away team stats

# dict to map team names between basketball-reference and teamrankings
name_dict = {
    "Atlanta Hawks": 'Atlanta',
    "Boston Celtics": 'Boston',
    "Brooklyn Nets": 'Brooklyn',
    "Charlotte Hornets": 'Charlotte',
    "Chicago Bulls": 'Chicago',
    "Cleveland Cavaliers": 'Cleveland',
    "Dallas Mavericks": 'Dallas',
    "Denver Nuggets": 'Denver',
    "Detroit Pistons": 'Detroit',
    "Golden State Warriors": 'Golden State',
    "Houston Rockets": 'Houston',
    "Indiana Pacers": 'Indiana',
    "Los Angeles Clippers": 'LA Clippers',
    "Los Angeles Lakers": 'LA Lakers',
    "Memphis Grizzlies": 'Memphis',
    "Miami Heat": 'Miami',
    "Milwaukee Bucks": 'Milwaukee',
    "Minnesota Timberwolves": 'Minnesota',
    "New Orleans Pelicans": 'New Orleans',
    "New York Knicks": 'New York',
    "Oklahoma City Thunder": 'Okla City',
    "Orlando Magic": 'Orlando',
    "Philadelphia 76ers": 'Philadelphia',
    "Phoenix Suns": 'Phoenix',
    "Portland Trail Blazers": 'Portland',
    "Sacramento Kings": 'Sacramento',
    "San Antonio Spurs": 'San Antonio',
    "Toronto Raptors": 'Toronto',
    "Utah Jazz": 'Utah',
    "Washington Wizards": 'Washington',
}

stats = ['points-per-game', 'true-shooting-percentage', 'offensive-rebounds-per-game', 'defensive-rebounds-per-game', 'steals-per-game', 'assist--per--turnover-ratio', 'personal-fouls-per-game', 'win-pct-all-games']
teams = ['Atlanta', 'Boston', 'Brooklyn', 'Charlotte', 'Chicago', 'Cleveland', 'Dallas', 'Denver', 'Detroit', 'Golden State', 'Houston', 'Indiana', 'LA Clippers', 'LA Lakers', 'Memphis', 'Miami', 'Milwaukee', 'Minnesota', 'New Orleans', 'New York', 'Okla City', 'Orlando', 'Philadelphia', 'Phoenix', 'Portland', 'Sacramento', 'San Antonio', 'Toronto', 'Utah', 'Washington']

def main():
    scrape_schedule()

def scrape_schedule():

    date = {
        "year": 2022,
        "month": 10,
        "day": 30
    }

    data = {}
    id = 0

    for i in range(0, 7):
        url = get_schedule_url(date['month'])
        if url == "Invalid month":
            print(url)
            return
        response = requests.get(url) 
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')

        for r in rows:
            game_date = r.find('a')
            if game_date:
                data[id] = {}
                game_date = format_date(game_date.get_text())
                home_team = r.find('td', attrs={'data-stat': 'home_team_name'}).get_text()
                away_team = r.find('td', attrs={'data-stat': 'visitor_team_name'}).get_text()
                data[id]['home_team'], data[id]['away_team'], data[id]['date'] = home_team, away_team, game_date
                date = create_date(game_date)

                home_pts = r.find('td', attrs={'data-stat': 'home_pts'}).get_text()
                away_pts = r.find('td', attrs={'data-stat': 'visitor_pts'}).get_text()

                outcome = 1 if int(home_pts) > int(away_pts) else 0

                data[id]['outcome'] = outcome

                cur_stats = get_stats_at_date(date, [name_dict[home_team], name_dict[away_team]])

                print(f'Game ID: {id}, home team: {home_team}, away team: {away_team}, date: {game_date}, outcome: {outcome}, homestats: {cur_stats[name_dict[home_team]]}, awaystats: {cur_stats[name_dict[away_team]]}')

                if cur_stats:              
                    data[id]['home_stats'] = cur_stats[name_dict[home_team]]
                    data[id]['away_stats'] = cur_stats[name_dict[away_team]]
                else:
                    print(f'Error: No stats found for game {id}')

                id += 1

        if date['month'] == 12:
            date['month'] = 1
            date['day'] = 1
            date['year'] += 1
            
        else:
            date['month'] += 1
            date['day'] = 1

    print_data(data)
    write_to_csv(data)


def get_stats_at_date(date, teams):
    data = {}
    for stat in stats:
        response = requests.get(get_stats_url(date, stat)) 
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        if not table:
            print(f"Error: No table found for stat at url: {get_stats_url(date, stat)} with teams {teams}")
            return None
        rows = table.find_all('tr')

        for r in rows:
            v = r.find('td', class_='text-right')
            team_element = r.find('a')
            if team_element and v and team_element.get_text() in teams:

                team_name, value = team_element.get_text(), v.get_text()
                if '%' in value: # remove trailing % sign
                    value = value[:-1]

                if team_name not in data:
                    data[team_name] = {stat: value}
                else:
                    data[team_name][stat] = value

        time.sleep(1)

    if not data:
        print(f"Error: No data found for stat at url: {get_stats_url(date, stat)} with team {teams}")
        return None

    return data


def format_date(date):
    datetime_obj = datetime.strptime(date, '%a, %b %d, %Y')
    formatted_date = datetime_obj.strftime('%m/%d/%y')
    return formatted_date

def create_date(date):
    date_parts = date.split('/')
    custom_date = {
        "year": 2000 + int(date_parts[2]),
        "month": int(date_parts[0]),
        "day": int(date_parts[1])
    }
    return custom_date

def print_data(data):
    for id, game_data in data.items():
        if 'date' in game_data:
            print(f"Game ID: {id}")
            print(f"Date: {game_data['date']}")
            print(f"Home Team: {game_data['home_team']}")
            print(f"\tHome Stats: {game_data['home_stats']}")
            print(f"Away Team: {game_data['away_team']}")
            print(f"\tAway Stats: {game_data['away_stats']}")
            print(f"Outcome: {'Win' if game_data['outcome'] == 1 else 'Loss'}")
            print()


def get_stats_url(date, stat):
    if date['month'] == 10 and date['day'] < 25:
        date['day'] = 30
    
    return f"https://www.teamrankings.com/nba/stat/{stat}?date={date['year']}-{date['month']}-{date['day']}"


def write_to_csv(data):
    filename = f'full-22-23-matchups.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        home_stats_header, away_stats_header = [f'home_{stat}' for stat in stats], [f'away_{stat}' for stat in stats]
        header = ['Game ID', 'Date', 'Home Team', 'Away Team', 'Outcome'] + home_stats_header + away_stats_header
        writer.writerow(header)  # Write header row

        for id, game_data in data.items():
            writer.writerow([id, game_data['date'], game_data['home_team'], game_data['away_team'], game_data['outcome']] + list(game_data['home_stats'].values()) + list(game_data['away_stats'].values()))

    print(f"CSV file '{filename}' created successfully.")


def get_schedule_url(month):
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
        return "Invalid month"
    
    m = months.get(month, "Invalid month")
    return f'https://www.basketball-reference.com/leagues/NBA_2023_games-{m.lower()}.html'


if __name__ == '__main__':
    main()

