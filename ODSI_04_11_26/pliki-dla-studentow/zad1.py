from common import STAGE_DIRECTORIES, apply_config, log_lines, request, restore_config, start_server

PATHS = ["/materialy/", "/materialy/notatka.txt", "/wewnetrzne/", "/wewnetrzne/plan.txt"]


def check_paths():
    results = {}
    for path in PATHS:
        status, _, body = request(path)
        results[path] = f"{status} (listing)" if "Index of" in body else str(status)
    return results


def zadanie_1():
    try:
        start_server()
        apply_config("")
        before = check_paths()
        apply_config(STAGE_DIRECTORIES)
        after = check_paths()
        denied = log_lines("AH01630")
    finally:
        restore_config()

    print(f"{'URL':26}{'before':16}after")
    for path in PATHS:
        print(f"{path:26}{before[path]:16}{after[path]}")
    print(f"\nLog: {denied[-1] if denied else 'no AH01630 entry'}")


if __name__ == "__main__":
    zadanie_1()
