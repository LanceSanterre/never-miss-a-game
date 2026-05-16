import pandas as pd
import shutil
from pathlib import Path
from datetime import date


PROJECT_ROOT = Path(__file__).resolve().parent.parent

GAME_DATA_PATH = PROJECT_ROOT / "game_data" / "games_data.csv"
TEAMS_PATH = PROJECT_ROOT / "teams" / "teams.txt"
EMAIL_OUTPUT_PATH = PROJECT_ROOT / "email_data" / "todays_games.csv"
OLD_GAME_DATA_DIR = PROJECT_ROOT / "old_game_data" / str(date.today())


def move_file(src_path, dest_dir=OLD_GAME_DATA_DIR):
    src = Path(src_path)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / src.name
    shutil.move(str(src), str(dest))
    return dest


def find_my_team_games(games, my_teams):
    return_text = []

    for team in my_teams:
        for _, row in games.iterrows():
            game = str(row.iloc[0])
            et_time = row.iloc[1]
            ways_to_watch = str(row.iloc[2]).split(" ")

            if team.lower() in game.lower():
                return_text.append([game, et_time, ways_to_watch])

    return return_text


if __name__ == "__main__":
    data = pd.read_csv(GAME_DATA_PATH)

    with open(TEAMS_PATH, "r") as f:
        teams = [line.strip() for line in f if line.strip()]

    print(teams)

    txt = find_my_team_games(data, teams)
    dataF = pd.DataFrame(txt, columns=["game", "time", "ways_to_watch"])

    move_file(GAME_DATA_PATH)

    EMAIL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataF.to_csv(EMAIL_OUTPUT_PATH, index=False)

    print("Done with SCRIPT")