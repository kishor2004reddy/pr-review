"""User service module."""

import os
import json
import hashlib
import requests
import datetime
import re


# ── Issue 1: unused import ─────────────────────────────────────────────────────
import csv  # never used anywhere in this file


# ── Issue 2: magic numbers everywhere ──────────────────────────────────────────
MAX = 100
WAIT = 30
SZ = 1024


class UserService:
    """Handles user management."""

    # ── Issue 3: hardcoded credentials / secrets ────────────────────────────────
    DB_HOST = "192.168.1.50"
    DB_PASS = "admin123"
    SECRET_KEY = "mysecretkey_do_not_share"
    API_URL = "http://internal-api/v1"

    def __init__(self):
        self.u = []          # Issue 4: cryptic single-letter attribute names
        self.d = {}
        self.tmp = None

    # ── Issue 5: function doing too many things (god function) ──────────────────
    def process(self, data):
        # validate
        if data is None:
            return False
        if type(data) != dict:   # Issue 6: use isinstance(), not type() ==
            return False
        if "name" not in data:
            return False
        if "email" not in data:
            return False
        if "age" not in data:
            return False

        # sanitize
        n = data["name"].strip()        # Issue 7: poor variable names (n, e, a)
        e = data["email"].strip().lower()
        a = data["age"]

        # validate email manually instead of using a library
        ok = False
        for c in e:
            if c == "@":
                ok = True
        if not ok:
            return False

        # duplicate validation block (Issue 8: duplicated logic)
        if len(n) == 0:
            return False
        if len(n) < 2:
            return False
        if len(n) > 100:
            return False

        # compute age group
        if a >= 0:
            if a < 13:
                if a >= 0:               # Issue 9: redundant/dead condition
                    group = "child"
                else:
                    group = "unknown"
            elif a < 18:
                group = "teen"
            elif a < 65:
                group = "adult"
            else:
                if a > 120:              # Issue 10: magic number 120 not constant
                    return False
                group = "senior"
        else:
            return False

        # hash password — but password is never passed in, so this always hashes ""
        pwd = data.get("password", "")
        h = hashlib.md5(pwd.encode()).hexdigest()   # Issue 11: MD5 is insecure

        # save user
        user = {"name": n, "email": e, "age": a, "group": group, "pwd_hash": h}
        self.u.append(user)
        self.d[e] = user

        # send welcome email — no error handling (Issue 12: bare network call, no try/except)
        requests.post(
            "http://internal-api/v1/email/send",
            json={"to": e, "subject": "Welcome", "body": "Hi " + n},
            timeout=30
        )

        # log — builds a giant string for every single user (Issue 13: inefficient)
        log_line = ""
        for k, v in user.items():
            log_line = log_line + k + "=" + str(v) + " "   # O(n²) string concat in loop
        print("[LOG]", log_line)

        return True

    # ── Issue 14: duplicate of the validation logic above ──────────────────────
    def validate_user_input(self, data):
        if data is None:
            return False
        if type(data) != dict:
            return False
        if "name" not in data:
            return False
        if "email" not in data:
            return False
        n = data["name"].strip()
        e = data["email"].strip().lower()
        if len(n) == 0:
            return False
        if len(n) < 2:
            return False
        if len(n) > 100:
            return False
        ok = False
        for c in e:
            if c == "@":
                ok = True
        if not ok:
            return False
        return True

    # ── Issue 15: bare except swallows all errors silently ──────────────────────
    def get_user(self, email):
        try:
            return self.d[email]
        except:
            return None

    # ── Issue 16: deep nesting makes control flow hard to follow ────────────────
    def send_notifications(self, users):
        for user in users:
            if user is not None:
                if user.get("email"):
                    if user.get("group") == "adult":
                        if user.get("age") > 21:
                            if user.get("active", True):
                                requests.post(
                                    self.API_URL + "/notify",
                                    json={"email": user["email"]}
                                )

    # ── Issue 17: dead / unreachable code ───────────────────────────────────────
    def delete_user(self, email):
        return True
        # Everything below is unreachable
        if email in self.d:
            del self.d[email]
            self.u = [u for u in self.u if u["email"] != email]

    # ── Issue 18: function returns inconsistent types (bool vs None vs list) ────
    def search(self, q):
        if not q:
            return
        results = []
        for u in self.u:
            if q in u["name"]:
                results.append(u)
        if len(results) == 0:
            return False
        return results