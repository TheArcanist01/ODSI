import getpass

from common import STAGE_CGI, STAGE_PANEL, apply_config, compose, request, restore_config, start_server

USER = "student"
CGI_PATH = "/cgi-bin/uprawnienia.cgi"


def format_response(label, response):
    status, _, body = response
    text = f"{label}: HTTP {status}"
    if status == 200:
        text += "\n" + "\n".join("  " + line for line in body.strip().splitlines())
    return text


def zadanie_3():
    password = getpass.getpass(f"Password for {USER}: ")
    try:
        start_server()
        apply_config(STAGE_PANEL)
        before = request(CGI_PATH)
        listing = compose("exec", "-T", "web", "ls", "-ln", "/lab-data/")
        users = compose("exec", "-T", "web", "id", "daemon")
        apply_config(STAGE_CGI)
        no_credentials = request(CGI_PATH)
        with_credentials = request(CGI_PATH, (USER, password))
    finally:
        restore_config()

    print(format_response("Before Basic", before))
    print(f"\nls -ln /lab-data/:\n{listing.strip()}\nid daemon: {users.strip()}\n")
    print(format_response("After Basic, no credentials", no_credentials))
    print(format_response("After Basic, correct password", with_credentials))


if __name__ == "__main__":
    zadanie_3()
