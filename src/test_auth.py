import unittest

from fastapi import HTTPException
from starlette.requests import Request

from app import (
    LoginCredentials,
    active_sessions,
    activities,
    login,
    logout,
    require_teacher,
    signup_for_activity,
    unregister_from_activity,
)
from auth import hash_password, verify_password
from unittest.mock import patch


def make_request(session=None):
    headers = []
    if session:
        token, username = next(iter(session.items()))
        active_sessions[token] = username
        headers.append((b"authorization", f"Bearer {token}".encode()))
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": headers,
        "query_string": b"",
    }
    return Request(scope)


class TeacherAuthenticationTests(unittest.TestCase):
    def test_password_hash_is_salted_and_verifiable(self):
        first_hash = hash_password("correct horse battery staple")
        second_hash = hash_password("correct horse battery staple")

        self.assertNotEqual(first_hash, second_hash)
        self.assertTrue(verify_password("correct horse battery staple", first_hash))
        self.assertFalse(verify_password("wrong password", first_hash))

    def test_unauthenticated_teacher_check_is_rejected(self):
        with self.assertRaises(HTTPException) as error:
            require_teacher(make_request())

        self.assertEqual(error.exception.status_code, 401)

    def test_login_issues_and_logout_revokes_session_token(self):
        password_hash = hash_password("correct horse battery staple")
        with patch("app.load_teacher_hashes", return_value={"coach": password_hash}):
            result = login(
                LoginCredentials(username="coach", password="correct horse battery staple"),
                make_request(),
            )

        token = result["token"]
        self.assertEqual(active_sessions[token], "coach")
        logout(make_request({token: "coach"}))
        self.assertNotIn(token, active_sessions)

    def test_login_rejects_invalid_password(self):
        password_hash = hash_password("correct horse battery staple")
        with patch("app.load_teacher_hashes", return_value={"coach": password_hash}):
            with self.assertRaises(HTTPException) as error:
                login(
                    LoginCredentials(username="coach", password="wrong password"),
                    make_request(),
                )

        self.assertEqual(error.exception.status_code, 401)

    def test_only_authenticated_teacher_can_change_roster(self):
        activity = "Chess Club"
        email = "new-student@mergington.edu"
        original_participants = activities[activity]["participants"].copy()

        try:
            with self.assertRaises(HTTPException) as error:
                signup_for_activity(activity, email, make_request())
            self.assertEqual(error.exception.status_code, 401)
            self.assertNotIn(email, activities[activity]["participants"])

            with self.assertRaises(HTTPException) as error:
                unregister_from_activity(activity, email, make_request())
            self.assertEqual(error.exception.status_code, 401)

            teacher_request = make_request({"test-token": "coach"})
            signup_for_activity(activity, email, teacher_request)
            self.assertIn(email, activities[activity]["participants"])
            unregister_from_activity(activity, email, teacher_request)
            self.assertNotIn(email, activities[activity]["participants"])
        finally:
            activities[activity]["participants"] = original_participants
            active_sessions.pop("test-token", None)


if __name__ == "__main__":
    unittest.main()