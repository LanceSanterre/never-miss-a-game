from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR   

SCRIPTS = [
    SCRIPTS_DIR / "get_todays_games.py",
    SCRIPTS_DIR / "team_info.py",
    SCRIPTS_DIR / "send_email.py",
]


def run_script(script_path: Path):
    print(f"\nRunning: {script_path.name}")

    if not script_path.exists():
        print(f"File not found: {script_path}")
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Script failed: {script_path.name}")
        print("---- STDOUT ----")
        print(result.stdout)
        print("---- STDERR ----")
        print(result.stderr)
        sys.exit(result.returncode)

    print(f"Finished: {script_path.name}")
    if result.stdout:
        print("---- Output ----")
        print(result.stdout)


def main():
    print("Starting pipeline...")

    for script in SCRIPTS:
        run_script(script)

    print("\nAll scripts completed successfully!")


if __name__ == "__main__":
    main()
