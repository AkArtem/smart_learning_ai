import subprocess
import os
import tempfile


def run_cmd(cmd, env=None):
    return subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        env=env,
    )


def test_full_cli_flow():
    with tempfile.TemporaryDirectory() as tmp:

        db_path = os.path.join(tmp, "test.db")
        env = os.environ.copy()
        env["DB_PATH"] = db_path

        r = run_cmd("python -m src.cli.main init", env)
        assert "initialized" in r.stdout.lower()

        r = run_cmd("python -m src.cli.main add-subject Math", env)
        assert "Math" in r.stdout

        r = run_cmd("python -m src.cli.main list-subjects", env)
        assert "Math" in r.stdout

        r = run_cmd(
            "python -m src.cli.main add-session 1 2026-02-11 "
            "--start-time 18:30 --duration 60 --focus 4",
            env,
        )
        assert "Added session" in r.stdout

        r = run_cmd("python -m src.cli.main list-sessions", env)
        assert "2026-02-11" in r.stdout

        r = run_cmd("python -m src.cli.main show-session 1", env)
        assert "Subject ID" in r.stdout

        r = run_cmd("python -m src.cli.main delete-session 1", env)
        assert "Deleted" in r.stdout
