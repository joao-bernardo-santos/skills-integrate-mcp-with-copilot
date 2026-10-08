import getpass
import json

from auth import TEACHERS_FILE, hash_password


def main():
    username = input("Teacher username: ").strip()
    if not username:
        raise SystemExit("Username cannot be empty")

    password = getpass.getpass("Teacher password (at least 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")

    if TEACHERS_FILE.exists():
        data = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    else:
        data = {"teachers": []}

    teachers = data.get("teachers")
    if not isinstance(teachers, list):
        raise SystemExit("teachers.json must contain a 'teachers' list")
    if any(teacher.get("username") == username for teacher in teachers):
        raise SystemExit("That username already exists")

    teachers.append({"username": username, "password_hash": hash_password(password)})
    TEACHERS_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    TEACHERS_FILE.chmod(0o600)
    print(f"Added teacher '{username}' to {TEACHERS_FILE}")


if __name__ == "__main__":
    main()