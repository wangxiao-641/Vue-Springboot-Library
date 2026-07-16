#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:9090").rstrip("/")
RUN_ID = str(int(time.time() * 1000))
READER_USERNAME = "cir_reader_" + RUN_ID
SECOND_READER_USERNAME = "cir_reader2_" + RUN_ID
BOOK_ISBN = "CIR-ISBN-" + RUN_ID
BOOK_NAME = "circulation-test-book-" + RUN_ID

created_reader_id = None
created_second_reader_id = None
created_book_id = None


def http_json(method, path, body=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode("utf-8")
            return resp.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        try:
            parsed = json.loads(text) if text else {}
        except json.JSONDecodeError:
            parsed = {"raw": text}
        return exc.code, parsed


def expect_code_zero(resp):
    return resp.get("code") in ("0", 0)


def get_records(path, params):
    query = urllib.parse.urlencode(params)
    status, resp = http_json("GET", path + "?" + query)
    if status != 200 or not expect_code_zero(resp):
        raise AssertionError("query failed: {} {}".format(status, resp))
    return resp.get("data", {}).get("records", [])


def find_book():
    records = get_records("/book", {
        "pageNum": 1,
        "pageSize": 50,
        "search1": BOOK_ISBN,
        "search2": "",
        "search3": "",
    })
    for record in records:
        if record.get("isbn") == BOOK_ISBN:
            return record
    return None


def current_records(reader_id=None):
    reader_id = reader_id if reader_id is not None else created_reader_id
    return [
        record for record in get_records("/bookwithuser", {
            "pageNum": 1,
            "pageSize": 50,
            "search1": BOOK_ISBN,
            "search2": "",
            "search3": reader_id or "",
        })
        if record.get("isbn") == BOOK_ISBN and record.get("id") == reader_id
    ]


def lend_records(reader_id=None):
    reader_id = reader_id if reader_id is not None else created_reader_id
    return [
        record for record in get_records("/LendRecord", {
            "pageNum": 1,
            "pageSize": 50,
            "search1": BOOK_ISBN,
            "search2": "",
            "search3": reader_id or "",
        })
        if record.get("isbn") == BOOK_ISBN and record.get("readerId") == reader_id
    ]


def create_reader(username, nick_name):
    status, resp = http_json("POST", "/user/register", {
        "username": username,
        "password": "test123",
        "nickName": nick_name,
        "role": 2,
    })
    if status != 200 or not expect_code_zero(resp):
        raise AssertionError("create reader failed: {} {}".format(status, resp))

    status, resp = http_json("POST", "/user/login", {
        "username": username,
        "password": "test123",
    })
    if status != 200 or not expect_code_zero(resp):
        raise AssertionError("login reader failed: {} {}".format(status, resp))
    reader_id = resp.get("data", {}).get("id")
    if not reader_id:
        raise AssertionError("reader id missing: {}".format(resp))
    return reader_id


def setup():
    global created_reader_id, created_second_reader_id, created_book_id

    created_reader_id = create_reader(READER_USERNAME, "Circulation Reader " + RUN_ID)
    created_second_reader_id = create_reader(SECOND_READER_USERNAME, "Circulation Reader 2 " + RUN_ID)

    status, resp = http_json("POST", "/book", {
        "isbn": BOOK_ISBN,
        "name": BOOK_NAME,
        "price": 1,
        "author": "circulation-test",
        "publisher": "circulation-test",
        "borrownum": 0,
        "totalCount": 1,
    })
    if status != 200 or not expect_code_zero(resp):
        raise AssertionError("create book failed: {} {}".format(status, resp))

    book = find_book()
    if not book:
        raise AssertionError("created book not found")
    created_book_id = book.get("id")


def cleanup():
    failures = []
    try:
        for reader_id in (created_reader_id, created_second_reader_id):
            if not reader_id:
                continue
            for current in current_records(reader_id):
                _, resp = http_json("POST", "/bookwithuser/deleteRecord", {
                    "id": current.get("id"),
                    "isbn": current.get("isbn"),
                })
                if not expect_code_zero(resp):
                    failures.append("delete current {}".format(resp))
    except Exception as exc:
        failures.append("query/delete current {}".format(exc))

    try:
        for reader_id in (created_reader_id, created_second_reader_id):
            if not reader_id:
                continue
            for record in lend_records(reader_id):
                _, resp = http_json("POST", "/LendRecord/deleteRecord", {
                    "isbn": record.get("isbn"),
                    "borrownum": record.get("borrownum"),
                })
                if not expect_code_zero(resp):
                    failures.append("delete lend record {}".format(resp))
    except Exception as exc:
        failures.append("query/delete lend records {}".format(exc))

    if created_book_id:
        _, resp = http_json("DELETE", "/book/{}".format(created_book_id))
        if not expect_code_zero(resp):
            failures.append("delete book {}".format(resp))

    if created_reader_id:
        _, resp = http_json("DELETE", "/user/{}".format(created_reader_id))
        if not expect_code_zero(resp):
            failures.append("delete reader {}".format(resp))

    if created_second_reader_id:
        _, resp = http_json("DELETE", "/user/{}".format(created_second_reader_id))
        if not expect_code_zero(resp):
            failures.append("delete second reader {}".format(resp))

    if failures:
        print("CLEANUP WARN: " + "; ".join(failures))


def parse_time(value):
    if not value:
        raise AssertionError("time value missing")
    value = value.replace("T", " ")
    return time.strptime(value[:19], "%Y-%m-%d %H:%M:%S")


def seconds_between(later, earlier):
    return time.mktime(parse_time(later)) - time.mktime(parse_time(earlier))


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def run_case(name, func):
    try:
        detail = func()
        print("PASS {} - {}".format(name, detail))
        return True
    except Exception as exc:
        print("FAIL {} - {}".format(name, exc))
        return False


def case_borrow_success():
    status, resp = http_json("POST", "/circulation/borrow", {
        "readerId": created_reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and expect_code_zero(resp), "borrow response {}".format(resp))
    book = find_book()
    currents = current_records()
    lends = lend_records()
    assert_true(book.get("availableCount") == 0, "availableCount={}".format(book.get("availableCount")))
    assert_true(book.get("status") == "0", "status={}".format(book.get("status")))
    assert_true(len(currents) == 1, "current count={}".format(len(currents)))
    assert_true(len(lends) == 1 and lends[0].get("status") == "0", "lend records={}".format(lends))
    return "availableCount=0, current=1, openRecord=1"


def case_borrow_no_stock_fails():
    before_book = find_book()
    before_currents = current_records()
    before_second_currents = current_records(created_second_reader_id)
    before_lends = lend_records()
    before_second_lends = lend_records(created_second_reader_id)
    status, resp = http_json("POST", "/circulation/borrow", {
        "readerId": created_second_reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and not expect_code_zero(resp), "expected failure response, got {}".format(resp))
    after_book = find_book()
    after_currents = current_records()
    after_second_currents = current_records(created_second_reader_id)
    after_lends = lend_records()
    after_second_lends = lend_records(created_second_reader_id)
    assert_true(after_book.get("availableCount") == before_book.get("availableCount"), "stock changed")
    assert_true(len(after_currents) == len(before_currents), "current count changed")
    assert_true(len(after_second_currents) == len(before_second_currents), "second reader current count changed")
    assert_true(len(after_lends) == len(before_lends), "lend count changed")
    assert_true(len(after_second_lends) == len(before_second_lends), "second reader lend count changed")
    return "failed without changing stock/current/history"


def case_first_renew_success():
    before = current_records()[0]
    status, resp = http_json("POST", "/circulation/renew", {
        "readerId": created_reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and expect_code_zero(resp), "renew response {}".format(resp))
    after = current_records()[0]
    delta = seconds_between(after.get("deadtime"), before.get("deadtime"))
    assert_true(29 * 86400 <= delta <= 31 * 86400, "deadtime delta seconds={}".format(delta))
    assert_true(after.get("prolong") == 0, "prolong={}".format(after.get("prolong")))
    return "deadtime extended about 30 days, prolong=0"


def case_second_renew_fails():
    before = current_records()[0]
    status, resp = http_json("POST", "/circulation/renew", {
        "readerId": created_reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and not expect_code_zero(resp), "expected failure response, got {}".format(resp))
    after = current_records()[0]
    assert_true(after.get("deadtime") == before.get("deadtime"), "deadtime changed")
    assert_true(after.get("prolong") == before.get("prolong"), "prolong changed")
    return "failed and deadtime stayed {}".format(after.get("deadtime"))


def case_return_success():
    status, resp = http_json("POST", "/circulation/return", {
        "readerId": created_reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and expect_code_zero(resp), "return response {}".format(resp))
    book = find_book()
    currents = current_records()
    lends = lend_records()
    returned = [record for record in lends if record.get("status") == "1"]
    assert_true(book.get("availableCount") == 1, "availableCount={}".format(book.get("availableCount")))
    assert_true(book.get("status") == "1", "status={}".format(book.get("status")))
    assert_true(len(currents) == 0, "current count={}".format(len(currents)))
    assert_true(len(returned) == 1 and returned[0].get("returnTime"), "returned records={}".format(returned))
    return "availableCount=1, current=0, history returned"


def case_repeat_return_fails():
    before_book = find_book()
    status, resp = http_json("POST", "/circulation/return", {
        "readerId": created_reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and not expect_code_zero(resp), "expected failure response, got {}".format(resp))
    after_book = find_book()
    assert_true(after_book.get("availableCount") == before_book.get("availableCount"), "stock changed")
    return "failed and availableCount stayed {}".format(after_book.get("availableCount"))


def main():
    failures = 0
    try:
        setup()
        cases = [
            ("borrow success", case_borrow_success),
            ("borrow without stock fails", case_borrow_no_stock_fails),
            ("first renew success", case_first_renew_success),
            ("second renew fails", case_second_renew_fails),
            ("return success", case_return_success),
            ("repeat return fails", case_repeat_return_fails),
        ]
        for name, func in cases:
            if not run_case(name, func):
                failures += 1
    except Exception as exc:
        failures += 1
        print("FAIL setup/runtime - {}".format(exc))
    finally:
        cleanup()

    if failures:
        print("RESULT FAIL - {} case(s) failed".format(failures))
        return 1
    print("RESULT PASS - all circulation HTTP cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
