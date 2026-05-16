import os
import re
import sys
import subprocess
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# -----------------------------
# Paths + Env
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # project root (one level above this file)
TEAM_FILE = PROJECT_ROOT / "teams.txt"
ENV_FILE = PROJECT_ROOT / ".env"

# If your scripts folder is actually named "scirpts", keep it.
# If it's "scripts", change it here.
SCRIPTS_DIR = PROJECT_ROOT / "scirpts"

PYTHON = sys.executable  # same python env as Streamlit

load_dotenv(dotenv_path=ENV_FILE)


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def append_unique_line(path: Path, value: str) -> bool:
    """
    Append value to file as a new line if it doesn't already exist.
    Returns True if appended, False if it already existed.
    """
    value = value.strip()
    if not value:
        return False

    existing = set(read_lines(path))
    if value in existing:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(value + "\n")
    return True


def upsert_env_key(env_path: Path, key: str, value: str) -> None:
    """
    Upsert KEY=VALUE in .env file (preserves other lines).
    """
    lines = []
    if env_path.exists():
        lines = env_path.read_text().splitlines()

    new_lines = []
    found = False
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            new_lines.append(line)
            continue

        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n")


def append_email_to_env(email: str) -> tuple[bool, str]:
    """
    Appends email to RECIPIENT_EMAIL in .env as comma-separated list.
    Returns (added?, new_value).
    """
    email = email.strip()
    current = os.getenv("RECIPIENT_EMAIL", "").strip()

    emails = {e.strip() for e in current.split(",") if e.strip()}
    if email in emails:
        return False, ",".join(sorted(emails))

    emails.add(email)
    new_value = ",".join(sorted(emails))

    upsert_env_key(ENV_FILE, "RECIPIENT_EMAIL", new_value)

    # Reload env so UI displays updated value without restarting Streamlit
    load_dotenv(dotenv_path=ENV_FILE, override=True)
    return True, new_value


def run_script(script_path: Path) -> tuple[int, str, str]:
    """
    Runs a script as a subprocess using the same python env.
    Returns: (return_code, stdout, stderr)
    """
    result = subprocess.run(
        [PYTHON, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Team + Email Config", page_icon="$$", layout="centered")
st.title(" Team + Email Config (Append Mode)")

team_input = st.text_input("Full team name", placeholder="San Jose Sharks")
email_input = st.text_input("Recipient email", placeholder="you@example.com")

if st.button("Add Team + Email", use_container_width=True):
    t = team_input.strip()
    e = email_input.strip()

    if not t:
        st.error("Team name required.")
    elif not e:
        st.error("Email required.")
    elif not is_valid_email(e):
        st.error("Invalid email format.")
    else:
        team_added = append_unique_line(TEAM_FILE, t)
        email_added, new_email_value = append_email_to_env(e)

        if team_added:
            st.success(f"Added team: {t}")
        else:
            st.info(f"Team already exists: {t}")

        if email_added:
            st.success(f"Added email: {e}")
        else:
            st.info(f"Email already exists: {e}")

st.divider()

# Display saved data
st.subheader("Saved Teams")
teams = read_lines(TEAM_FILE)
if teams:
    for t in teams:
        st.write(f"- {t}")
else:
    st.write("(none)")

st.subheader("Saved Emails")
saved_emails_raw = os.getenv("RECIPIENT_EMAIL", "").strip()
if saved_emails_raw:
    for e in [x.strip() for x in saved_emails_raw.split(",") if x.strip()]:
        st.write(f"- {e}")
else:
    st.write("(none)")

st.divider()

# Run Automation
st.title("Run Automation")

SCRIPTS = [
    SCRIPTS_DIR / "get_todays_games.py",
    SCRIPTS_DIR / "team_info.py",
    SCRIPTS_DIR / "send_email.py",
]

# guard: show missing scripts clearly
missing = [str(p) for p in SCRIPTS if not p.exists()]
if missing:
    st.warning("Some scripts were not found. Fix paths or folder name:")
    for m in missing:
        st.code(m)
    st.stop()

if "running" not in st.session_state:
    st.session_state.running = False

run_clicked = st.button("Run all scripts", use_container_width=True, disabled=st.session_state.running)

if run_clicked and not st.session_state.running:
    st.session_state.running = True
    try:
        st.info("Running scripts in order...")

        for script in SCRIPTS:
            st.write(f"### Running `{script.name}`")

            code, out, err = run_script(script)

            if out.strip():
                st.code(out, language="text")

            if code != 0:
                st.error(f"`{script.name}` failed (exit code {code})")
                if err.strip():
                    st.code(err, language="text")
                st.stop()
            else:
                st.success(f"`{script.name}` completed successfully ")

        st.success("All scripts finished")

    finally:
        st.session_state.running = False
