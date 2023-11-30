from bs4 import BeautifulSoup
import requests
import csv

'''
https://www.teamrankings.com/nba/stat/true-shooting-percentage?date=2022-10-30
'''
url = 'https://www.teamrankings.com/nba/stat/true-shooting-percentage?date=2022-10-30'

stats = ['points-per-game', 'true-shooting-percentage', 'offensive-rebounds-per-game', 'defensive-rebounds-per-game', 'steals-per-game', 'assist--per--turnover-ratio', 'personal-fouls-per-game', 'win-pct-all-games']
teams = ['Atlanta', 'Boston', 'Brooklyn', 'Charlotte', 'Chicago', 'Cleveland', 'Dallas', 'Denver', 'Detroit', 'Golden State', 'Houston', 'Indiana', 'LA Clippers', 'LA Lakers', 'Memphis', 'Miami', 'Milwaukee', 'Minnesota', 'New Orleans', 'New York', 'Okla City', 'Orlando', 'Philadelphia', 'Phoenix', 'Portland', 'Sacramento', 'San Antonio', 'Toronto', 'Utah', 'Washington']

# Start date of 2022-2023 NBA season
date = {
    "year": 2022,
    "month": 10,
    "day": 30
}

def main():
    scrape(stats)

def scrape(stats):
    data = {}

    for i in range(0, 7):
        for stat in stats:
            print(f'stat = {stat}')
            response = requests.get(format_url(date, stat)) 
            html_content = response.text

            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table')
            rows = table.find_all('tr')


            for r in rows:
                v = r.find('td', class_='text-right')
                team = r.find('a')
                if team and v:

                    team_name, value = team.get_text(), v.get_text()
                    if '%' in value:
                        value = value[:-1]

                    if team_name not in data:
                        data[team_name] = {stat: value}
                    else:
                        data[team_name][stat] = value

                if not data:
                    print(f'No data found for stat at url: {format_url(date, stat)} ')

        write_to_csv(data, date)

        if date['month'] == 12:
            date['month'] = 1
            date['year'] += 1
        else:
            date['month'] += 1

    return data
    
    
def write_to_csv(data, date): 

    filename = f'22-23-monthly/{format_date(date)}.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        stats = list(list(data.items())[0][1].keys())
        header = ['Team'] + stats
        writer.writerow(header)  # Write header row

        for team, stats in data.items():
            writer.writerow([team] + list(stats.values()))  # Write team name and stats

    print(f"CSV file '{filename}' created successfully.")


def format_date(date):
    return f"{date['year']}-{date['month']}-{date['day']}"

def format_url(date, stat):
    return f"https://www.teamrankings.com/nba/stat/{stat}?date={format_date(date)}"


if __name__ == '__main__':
    main()