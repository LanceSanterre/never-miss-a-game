# Never Miss a Game

A Python automation tool that scrapes daily sports schedules, filters games for your favorite teams, and sends you an email when they are playing.

---

## What This Project Does

This project runs a daily pipeline that:

1. Scrapes the current day's sports games from an online schedule  
2. Stores the full schedule as a CSV file  
3. Reads a list of user-selected teams  
4. Filters the schedule to only include those teams  
5. Outputs the filtered games to a new CSV file  
6. Sends an email notification with the results  
7. Archives the original data for record keeping  

### ETL Pipeline

- **Extract**: scrape daily game data  
- **Transform**: filter based on user-defined teams  
- **Load**: save structured outputs and send notifications  

---

## Project Structure

```text
never-miss-a-game/
├── scripts/
│   ├── get_todays_games.py
│   ├── team_info.py
│   ├── send_email.py
│   ├── conductor.py
│   └── cron_conductor.py
├── game_data/
├── email_data/
├── old_game_data/
├── teams/
│   └── teams.txt
├── .gitignore
└── README.md


