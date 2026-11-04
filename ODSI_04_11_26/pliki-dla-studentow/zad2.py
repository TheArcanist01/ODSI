import getpass

from common import STAGE_PANEL, apply_config, compose, request, restore_config, start_server

USER = "student"


def zadanie_2():
    start_server()
    if compose("run", "--rm", "--no-deps", "narzedzia", "-cB", "/auth/uzytkownicy", USER, interactive=True) != 0:
        raise SystemExit("htpasswd failed")
    password = getpass.getpass(f"Password for {USER} (for tests): ")
    tests = [
        ("no credentials", "/panel/raport.txt", None),
        ("wrong password", "/panel/raport.txt", (USER, password + "-wrong")),
        ("correct password", "/panel/raport.txt", (USER, password)),
        ("public page", "/", None),
    ]
    try:
        start_server()
        apply_config(STAGE_PANEL)
        results = [(label, path, *request(path, credentials)) for label, path, credentials in tests]
    finally:
        restore_config()

    for label, path, status, headers, body in results:
        print(f"{label:18}{path:20}{status}")
    print(f"\nWWW-Authenticate (no credentials): {results[0][3].get('WWW-Authenticate')}")
    print(f"Body with correct password: {results[2][4].strip()}")


if __name__ == "__main__":
    zadanie_2()
