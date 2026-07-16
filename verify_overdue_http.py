#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:9090").rstrip("/")
BUSINESS_ZONE = ZoneInfo("Asia/Shanghai")
RUN_ID = "{}-{}".format(int(time.time() * 1000), os.getpid())
READER_USERNAME = "overdue_reader_" + RUN_ID
ADMIN_USERNAME = "overdue_admin_" + RUN_ID
OVERDUE_ISBN = "OVERDUE-A-" + RUN_ID
OTHER_ISBN = "OVERDUE-B-" + RUN_ID

reader_id = None
admin_id = None
book_ids = {}


def http_json(method, path, body=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            text = response.read().decode("utf-8")
            return response.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        try:
            payload = json.loads(text) if text else {}
        except json.JSONDecodeError:
            payload = {"raw": text}
        return exc.code, payload


def code_zero(response):
    return response.get("code") in ("0", 0)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def records(path, **params):
    query = urllib.parse.urlencode(params)
    status, response = http_json("GET", path + "?" + query)
    assert_true(status == 200 and code_zero(response), "query failed {} {}".format(status, response))
    return response.get("data", {}).get("records", [])


def find_book(isbn):
    matches = records("/book", pageNum=1, pageSize=50, search1=isbn, search2="", search3="")
    return next((item for item in matches if item.get("isbn") == isbn), None)


def current_loans(isbn="", overdue_only=False):
    return [
        item for item in records(
            "/bookwithuser",
            pageNum=1,
            pageSize=50,
            search1=isbn,
            search2="",
            search3=reader_id or "",
            overdueOnly=str(overdue_only).lower(),
        )
        if item.get("id") == reader_id and (not isbn or item.get("isbn") == isbn)
    ]


def lend_history(isbn="", overdue_only=False):
    return [
        item for item in records(
            "/LendRecord",
            pageNum=1,
            pageSize=50,
            search1=isbn,
            search2="",
            search3=reader_id or "",
            overdueOnly=str(overdue_only).lower(),
        )
        if item.get("readerId") == reader_id and (not isbn or item.get("isbn") == isbn)
    ]


def create_book(isbn, name):
    status, response = http_json("POST", "/book", {
        "isbn": isbn,
        "name": name,
        "price": 1,
        "author": "overdue-http-test",
        "publisher": "overdue-http-test",
        "totalCount": 1,
    })
    assert_true(status == 200 and code_zero(response), "create book failed {}".format(response))
    book = find_book(isbn)
    assert_true(book is not None, "created book not found {}".format(isbn))
    book_ids[isbn] = book.get("id")


def setup():
    global reader_id, admin_id
    status, response = http_json("POST", "/user/register", {
        "username": ADMIN_USERNAME,
        "password": "test123",
        "nickName": "Overdue Admin " + RUN_ID,
        "role": 1,
    })
    assert_true(status == 200 and code_zero(response), "register admin failed {}".format(response))
    status, response = http_json("POST", "/user/login", {
        "username": ADMIN_USERNAME,
        "password": "test123",
    })
    assert_true(status == 200 and code_zero(response), "login admin failed {}".format(response))
    admin_id = response.get("data", {}).get("id")
    assert_true(admin_id is not None, "admin id missing")
    status, response = http_json("POST", "/user/register", {
        "username": READER_USERNAME,
        "password": "test123",
        "nickName": "Overdue Reader " + RUN_ID,
        "role": 2,
    })
    assert_true(status == 200 and code_zero(response), "register reader failed {}".format(response))
    status, response = http_json("POST", "/user/login", {
        "username": READER_USERNAME,
        "password": "test123",
    })
    assert_true(status == 200 and code_zero(response), "login reader failed {}".format(response))
    reader_id = response.get("data", {}).get("id")
    assert_true(reader_id is not None, "reader id missing")
    create_book(OVERDUE_ISBN, "overdue-source-" + RUN_ID)
    create_book(OTHER_ISBN, "overdue-other-" + RUN_ID)


def cleanup():
    warnings = []
    if reader_id:
        try:
            for current in current_loans():
                _, response = http_json("POST", "/circulation/return", {
                    "readerId": reader_id,
                    "isbn": current.get("isbn"),
                })
                if not code_zero(response):
                    _, delete_response = http_json("POST", "/bookwithuser/deleteRecord", {
                        "id": reader_id,
                        "isbn": current.get("isbn"),
                    })
                    if not code_zero(delete_response):
                        warnings.append("delete current {}".format(delete_response))
        except Exception as exc:
            warnings.append("return current loans {}".format(exc))
        try:
            for history in lend_history():
                _, response = http_json("POST", "/LendRecord/deleteRecord", {
                    "isbn": history.get("isbn"),
                    "borrownum": history.get("borrownum"),
                })
                if not code_zero(response):
                    warnings.append("delete history {}".format(response))
        except Exception as exc:
            warnings.append("delete histories {}".format(exc))
    for isbn, book_id in book_ids.items():
        _, response = http_json("DELETE", "/book/{}".format(book_id))
        if not code_zero(response):
            warnings.append("delete book {} {}".format(isbn, response))
    if reader_id:
        _, response = http_json("DELETE", "/user/{}".format(reader_id))
        if not code_zero(response):
            warnings.append("delete reader {}".format(response))
    if admin_id:
        _, response = http_json("DELETE", "/user/{}".format(admin_id))
        if not code_zero(response):
            warnings.append("delete admin {}".format(response))
    if warnings:
        print("CLEANUP WARN - " + "; ".join(warnings))


def parse_business_time(value):
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=BUSINESS_ZONE)


def borrow(isbn):
    return http_json("POST", "/circulation/borrow", {"readerId": reader_id, "isbn": isbn})


def case_due_date_generated_by_backend():
    status, response = borrow(OVERDUE_ISBN)
    assert_true(status == 200 and code_zero(response), "borrow failed {}".format(response))
    current = current_loans(OVERDUE_ISBN)
    assert_true(len(current) == 1, "current loans {}".format(current))
    loan = current[0]
    lend_time = parse_business_time(loan.get("lendtime"))
    due_time = parse_business_time(loan.get("deadtime"))
    assert_true(due_time == lend_time + timedelta(days=30), "lend={} due={}".format(lend_time, due_time))
    assert_true(loan.get("dueStatus") == "NORMAL", "status {}".format(loan))
    return "deadtime is exactly lendtime + 30 days and request contained no date"


def case_adjust_yesterday_becomes_overdue():
    loan = current_loans(OVERDUE_ISBN)[0]
    today = datetime.now(BUSINESS_ZONE).date()
    yesterday = today - timedelta(days=1)
    adjusted = yesterday.strftime("%Y-%m-%d") + " 12:00:00"
    status, response = http_json("POST", "/bookwithuser", {
        "borrowId": loan.get("borrowId"),
        "deadtime": adjusted,
        "prolong": 99,
    })
    assert_true(status == 200 and not code_zero(response), "arbitrary update was accepted {}".format(response))
    unchanged = current_loans(OVERDUE_ISBN)[0]
    assert_true(unchanged.get("deadtime") == loan.get("deadtime"), "arbitrary update changed deadtime")
    assert_true(unchanged.get("prolong") == loan.get("prolong"), "arbitrary update changed prolong")
    status, response = http_json("PUT", "/bookwithuser/due-date", {
        "operatorId": reader_id,
        "borrowId": loan.get("borrowId"),
        "dueDate": adjusted,
    })
    assert_true(status == 200 and not code_zero(response), "reader adjustment was accepted {}".format(response))
    due_soon = (today + timedelta(days=3)).strftime("%Y-%m-%d") + " 12:00:00"
    status, response = http_json("PUT", "/bookwithuser/due-date", {
        "operatorId": admin_id,
        "borrowId": loan.get("borrowId"),
        "dueDate": due_soon,
    })
    assert_true(status == 200 and code_zero(response), "due-soon adjustment failed {}".format(response))
    assert_true(current_loans(OVERDUE_ISBN)[0].get("dueStatus") == "DUE_SOON", "three-day boundary is not DUE_SOON")
    normal = (today + timedelta(days=4)).strftime("%Y-%m-%d") + " 12:00:00"
    status, response = http_json("PUT", "/bookwithuser/due-date", {
        "operatorId": admin_id,
        "borrowId": loan.get("borrowId"),
        "dueDate": normal,
    })
    assert_true(status == 200 and code_zero(response), "normal adjustment failed {}".format(response))
    assert_true(current_loans(OVERDUE_ISBN)[0].get("dueStatus") == "NORMAL", "four-day boundary is not NORMAL")
    status, response = http_json("PUT", "/bookwithuser/due-date", {
        "operatorId": admin_id,
        "borrowId": loan.get("borrowId"),
        "dueDate": adjusted,
    })
    assert_true(status == 200 and code_zero(response), "adjust failed {}".format(response))
    after = current_loans(OVERDUE_ISBN)[0]
    assert_true(after.get("deadtime") == adjusted, "deadtime {}".format(after.get("deadtime")))
    assert_true(after.get("dueStatus") == "OVERDUE", "status {}".format(after.get("dueStatus")))
    assert_true((after.get("overdueDays") or 0) >= 1, "overdueDays {}".format(after.get("overdueDays")))
    return "arbitrary/non-admin writes rejected; +3=DUE_SOON, +4=NORMAL, yesterday=OVERDUE({} day)".format(after.get("overdueDays"))


def case_new_borrow_rejected_unchanged():
    before_book = find_book(OTHER_ISBN)
    before_current = current_loans()
    before_history = lend_history()
    status, response = borrow(OTHER_ISBN)
    assert_true(status == 200 and not code_zero(response), "expected rejection {}".format(response))
    after_book = find_book(OTHER_ISBN)
    assert_true(after_book.get("availableCount") == before_book.get("availableCount"), "stock changed")
    assert_true(after_book.get("borrownum") == before_book.get("borrownum"), "borrownum changed")
    assert_true(current_loans() == before_current, "current loans changed")
    assert_true(lend_history() == before_history, "lend history changed")
    return "borrow rejected and stock/current/history stayed unchanged"


def case_overdue_renew_rejected_unchanged():
    before = current_loans(OVERDUE_ISBN)[0]
    status, response = http_json("POST", "/circulation/renew", {
        "readerId": reader_id,
        "isbn": OVERDUE_ISBN,
    })
    assert_true(status == 200 and not code_zero(response), "expected rejection {}".format(response))
    after = current_loans(OVERDUE_ISBN)[0]
    assert_true(after.get("deadtime") == before.get("deadtime"), "deadtime changed")
    assert_true(after.get("prolong") == before.get("prolong"), "prolong changed")
    return "renew rejected and deadtime/prolong stayed unchanged"


def case_overdue_filters_include_record():
    currents = current_loans(overdue_only=True)
    histories = lend_history(overdue_only=True)
    assert_true(any(item.get("isbn") == OVERDUE_ISBN for item in currents), "current overdue filter {}".format(currents))
    assert_true(any(item.get("isbn") == OVERDUE_ISBN for item in histories), "history overdue filter {}".format(histories))
    assert_true(all(item.get("dueStatus") == "OVERDUE" for item in currents), "non-overdue current returned")
    assert_true(all(item.get("dueStatus") == "OVERDUE" for item in histories), "non-overdue history returned")
    return "current-loan and lend-history overdue filters both include the record"


def case_return_unlocks_borrowing():
    status, response = http_json("POST", "/circulation/return", {
        "readerId": reader_id,
        "isbn": OVERDUE_ISBN,
    })
    assert_true(status == 200 and code_zero(response), "return failed {}".format(response))
    status, response = borrow(OTHER_ISBN)
    assert_true(status == 200 and code_zero(response), "borrow after return failed {}".format(response))
    assert_true(len(current_loans(OTHER_ISBN)) == 1, "other book current loan missing")
    return "overdue book returned and another book borrowed successfully"


def run_case(name, function):
    try:
        detail = function()
        print("PASS {} - {}".format(name, detail))
        return True
    except Exception as exc:
        print("FAIL {} - {}".format(name, exc))
        return False


def main():
    failures = 0
    try:
        setup()
        cases = [
            ("backend generated +30 day due date", case_due_date_generated_by_backend),
            ("admin adjustment to yesterday", case_adjust_yesterday_becomes_overdue),
            ("overdue reader new borrow rejected unchanged", case_new_borrow_rejected_unchanged),
            ("overdue renewal rejected unchanged", case_overdue_renew_rejected_unchanged),
            ("overdue filters", case_overdue_filters_include_record),
            ("return automatically removes restriction", case_return_unlocks_borrowing),
        ]
        for name, function in cases:
            if not run_case(name, function):
                failures += 1
    except Exception as exc:
        failures += 1
        print("FAIL setup/runtime - {}".format(exc))
    finally:
        cleanup()
    if failures:
        print("RESULT FAIL - {} case(s) failed".format(failures))
        return 1
    print("RESULT PASS - all overdue HTTP cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
