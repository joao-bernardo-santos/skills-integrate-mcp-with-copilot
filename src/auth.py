import hashlib
import hmac
import json
import secrets
from pathlib import Path


TEACHERS_FILE = Path(__file__).with_name("teachers.json")
PBKDF2_ITERATIONS = 600_000


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, encoded_hash):
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        expected_digest = bytes.fromhex(digest_hex)
        actual_digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
    except (AttributeError, TypeError, ValueError):
        return False
    return hmac.compare_digest(actual_digest, expected_digest)


def load_teacher_hashes():
    try:
        data = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}

    teachers = data.get("teachers") if isinstance(data, dict) else None
    if not isinstance(teachers, list):
        raise ValueError("teachers.json must contain a 'teachers' list")

    hashes = {}
    for teacher in teachers:
        if not isinstance(teacher, dict):
            raise ValueError("Each teacher entry must be an object")
        username = teacher.get("username")
        password_hash = teacher.get("password_hash")
        if not isinstance(username, str) or not username or not isinstance(password_hash, str):
            raise ValueError("Each teacher needs a username and password_hash")
        if username in hashes:
            raise ValueError(f"Duplicate teacher username: {username}")
        hashes[username] = password_hash
    return hashes