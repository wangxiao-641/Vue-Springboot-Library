#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:9090").rstrip("/")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORDS = [os.environ.get("ADMIN_PASSWORD", "admin")]
if "ADMIN_PASSWORD" not in os.environ and "123456" not in ADMIN_PASSWORDS:
    ADMIN_PASSWORDS.append("123456")

RUN_ID = "{}-{}".format(int(time.time() * 1000), os.getpid())
READER_USERNAME = "usr_reader_" + RUN_ID.replace("-", "_")
READER_PASSWORD = "UsrPass_" + RUN_ID
READER_NAME = "用户验收读者" + RUN_ID
BOOK_ISBN = "USR-ISBN-" + RUN_ID
BOOK_NAME = "user-management-test-book-" + RUN_ID
FORBIDDEN_USERNAME = "usr_forbidden_" + RUN_ID.replace("-", "_")

admin_id = None
reader_id = None
book_id = None


def http_json(method, path, body=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
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


def ok(response):
    return response.get("code") in ("0", 0)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def records(path, **params):
    query = urllib.parse.urlencode(params)
    status, response = http_json("GET", path + "?" + query)
    assert_true(status == 200 and ok(response), "query failed {} {}".format(status, response))
    return response.get("data", {}).get("records", [])


def find_reader():
    matches = records(
        "/user/usersearch",
        pageNum=1,
        pageSize=100,
        search1="",
        search2=READER_NAME,
        search3="",
        search4="",
    )
    return next((item for item in matches if item.get("username") == READER_USERNAME), None)


def find_book():
    matches = records(
        "/book",
        pageNum=1,
        pageSize=100,
        search1=BOOK_ISBN,
        search2="",
        search3="",
    )
    return next((item for item in matches if item.get("isbn") == BOOK_ISBN), None)


def current_loans():
    if not reader_id:
        return []
    return [
        item for item in records(
            "/bookwithuser",
            pageNum=1,
            pageSize=100,
            search1=BOOK_ISBN,
            search2="",
            search3=reader_id,
        )
        if item.get("id") == reader_id and item.get("isbn") == BOOK_ISBN
    ]


def lend_records():
    if not reader_id:
        return []
    return [
        item for item in records(
            "/LendRecord",
            pageNum=1,
            pageSize=100,
            search1=BOOK_ISBN,
            search2="",
            search3=reader_id,
        )
        if item.get("readerId") == reader_id and item.get("isbn") == BOOK_ISBN
    ]


def login(username, password):
    return http_json("POST", "/user/login", {"username": username, "password": password})


def setup():
    global admin_id
    attempts = []
    for password in ADMIN_PASSWORDS:
        status, response = login(ADMIN_USERNAME, password)
        attempts.append("{}:{}".format(status, response.get("msg", response.get("code"))))
        if status == 200 and ok(response):
            admin_id = response.get("data", {}).get("id")
            role = response.get("data", {}).get("role")
            assert_true(admin_id is not None and role == 1, "configured account is not an administrator")
            return
    raise AssertionError(
        "administrator login failed; set ADMIN_USERNAME/ADMIN_PASSWORD. attempts={}".format(attempts)
    )


def cleanup():
    warnings = []
    if reader_id:
        try:
            for current in current_loans():
                _, response = http_json("POST", "/circulation/return", {
                    "readerId": reader_id,
                    "isbn": current.get("isbn"),
                })
                if not ok(response):
                    warnings.append("return current {}".format(response))
        except Exception as exc:
            warnings.append("query/return current {}".format(exc))

        try:
            _, response = login(READER_USERNAME, READER_PASSWORD)
            if ok(response):
                _, response = http_json(
                    "DELETE",
                    "/user/{}?{}".format(reader_id, urllib.parse.urlencode({"operatorId": admin_id})),
                )
                if not ok(response):
                    warnings.append("delete reader {}".format(response))
        except Exception as exc:
            warnings.append("delete reader {}".format(exc))

        try:
            for history in lend_records():
                _, response = http_json("POST", "/LendRecord/deleteRecord", {
                    "isbn": history.get("isbn"),
                    "borrownum": history.get("borrownum"),
                })
                if not ok(response):
                    warnings.append("delete history {}".format(response))
        except Exception as exc:
            warnings.append("delete history {}".format(exc))

    if book_id:
        _, response = http_json("DELETE", "/book/{}".format(book_id))
        if not ok(response):
            warnings.append("delete book {}".format(response))

    if warnings:
        print("CLEANUP WARN - " + "; ".join(warnings))
    return warnings


def run_case(name, function):
    try:
        detail = function()
        print("PASS {} - {}".format(name, detail))
        return True
    except Exception as exc:
        print("FAIL {} - {}".format(name, exc))
        return False


def case_admin_creates_reader():
    global reader_id
    status, response = http_json("POST", "/user", {
        "operatorId": admin_id,
        "username": READER_USERNAME,
        "password": READER_PASSWORD,
        "nickName": READER_NAME,
        "phone": "13800000000",
        "sex": "男",
        "address": "HTTP黑盒验收",
        "role": 2,
    })
    assert_true(status == 200 and ok(response), "create reader failed {} {}".format(status, response))
    reader = find_reader()
    assert_true(reader is not None and reader.get("role") == 2, "created reader not found or wrong role")
    reader_id = reader.get("id")
    assert_true(reader_id is not None, "created reader id missing")

    status, forbidden = http_json("POST", "/user", {
        "operatorId": admin_id,
        "username": READER_USERNAME + "_admin",
        "password": READER_PASSWORD,
        "nickName": READER_NAME,
        "role": 1,
    })
    assert_true(status == 200 and not ok(forbidden), "reader entry accepted role=1 {}".format(forbidden))
    return "reader id={} created with fixed role=2; role=1 rejected".format(reader_id)


def case_required_field_validation():
    invalid_payloads = [
        ({"username": "bad name", "password": READER_PASSWORD, "nickName": "测试"}, "username"),
        ({"username": FORBIDDEN_USERNAME, "password": "123", "nickName": "测试"}, "password"),
        ({"username": FORBIDDEN_USERNAME, "password": READER_PASSWORD, "nickName": "  "}, "name"),
    ]
    for fields, description in invalid_payloads:
        payload = {"operatorId": admin_id, "role": 2}
        payload.update(fields)
        status, response = http_json("POST", "/user", payload)
        assert_true(status == 200 and not ok(response), "invalid {} accepted {}".format(description, response))
    return "invalid username, password, and blank name all rejected"


def case_created_reader_can_login():
    status, response = login(READER_USERNAME, READER_PASSWORD)
    assert_true(status == 200 and ok(response), "created reader login failed {}".format(response))
    assert_true(response.get("data", {}).get("id") == reader_id, "login returned wrong reader")
    return "configured initial password works"


def case_duplicate_username_rejected():
    status, response = http_json("POST", "/user", {
        "operatorId": admin_id,
        "username": READER_USERNAME,
        "password": READER_PASSWORD,
        "nickName": READER_NAME + "重复",
        "role": 2,
    })
    assert_true(status == 200 and not ok(response), "duplicate username accepted {}".format(response))
    assert_true("重复" in response.get("msg", ""), "duplicate reason not explicit {}".format(response))
    matches = [item for item in records(
        "/user/usersearch",
        pageNum=1,
        pageSize=100,
        search1="",
        search2="",
        search3="",
        search4="",
    ) if item.get("username") == READER_USERNAME]
    assert_true(len(matches) == 1, "duplicate account count={}".format(len(matches)))
    return "duplicate rejected and exactly one account remains"


def case_permission_and_batch_guards():
    status, response = http_json("POST", "/user", {
        "operatorId": reader_id,
        "username": FORBIDDEN_USERNAME,
        "password": READER_PASSWORD,
        "nickName": "不应创建",
        "role": 2,
    })
    assert_true(status == 200 and not ok(response), "reader operator created an account {}".format(response))

    admin_delete_path = "/user/{}?{}".format(admin_id, urllib.parse.urlencode({"operatorId": admin_id}))
    status, response = http_json("DELETE", admin_delete_path)
    assert_true(status == 200 and not ok(response), "administrator was deleted through reader endpoint {}".format(response))

    status, response = http_json("POST", "/user/deleteBatch", [reader_id])
    assert_true(status == 200 and not ok(response), "batch delete was accepted {}".format(response))
    status, login_response = login(READER_USERNAME, READER_PASSWORD)
    assert_true(status == 200 and ok(login_response), "batch guard changed reader account")
    return "reader operator, administrator target, and legacy batch delete all rejected"


def case_active_loan_blocks_delete():
    global book_id
    status, response = http_json("POST", "/book", {
        "isbn": BOOK_ISBN,
        "name": BOOK_NAME,
        "price": 1,
        "author": "user-management-http-test",
        "publisher": "user-management-http-test",
        "totalCount": 1,
    })
    assert_true(status == 200 and ok(response), "create book failed {}".format(response))
    book = find_book()
    assert_true(book is not None, "created book not found")
    book_id = book.get("id")

    status, response = http_json("POST", "/circulation/borrow", {
        "readerId": reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and ok(response), "borrow failed {}".format(response))
    assert_true(len(current_loans()) == 1, "current loan missing")

    delete_path = "/user/{}?{}".format(reader_id, urllib.parse.urlencode({"operatorId": admin_id}))
    status, response = http_json("DELETE", delete_path)
    assert_true(status == 200 and not ok(response), "active reader deleted {}".format(response))
    assert_true("未归还" in response.get("msg", ""), "active-loan reason not explicit {}".format(response))
    status, login_response = login(READER_USERNAME, READER_PASSWORD)
    assert_true(status == 200 and ok(login_response), "reader cannot login after rejected delete")
    return "delete rejected and account still logs in"


def case_return_then_delete_succeeds():
    status, response = http_json("POST", "/circulation/return", {
        "readerId": reader_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and ok(response), "return failed {}".format(response))
    assert_true(not current_loans(), "current loan still exists after return")

    delete_path = "/user/{}?{}".format(reader_id, urllib.parse.urlencode({"operatorId": admin_id}))
    status, response = http_json("DELETE", delete_path)
    assert_true(status == 200 and ok(response), "delete after return failed {}".format(response))
    assert_true(find_reader() is None, "deleted reader still appears in list")
    status, login_response = login(READER_USERNAME, READER_PASSWORD)
    assert_true(status == 200 and not ok(login_response), "deleted reader still logs in {}".format(login_response))
    return "returned, deleted, absent from list, and login rejected"


def main():
    failures = 0
    cleanup_failures = []
    try:
        setup()
        cases = [
            ("admin creates temporary reader", case_admin_creates_reader),
            ("required field validation", case_required_field_validation),
            ("created reader can login", case_created_reader_can_login),
            ("duplicate username rejected", case_duplicate_username_rejected),
            ("permission and batch guards", case_permission_and_batch_guards),
            ("active loan blocks delete", case_active_loan_blocks_delete),
            ("return then delete succeeds", case_return_then_delete_succeeds),
        ]
        for name, function in cases:
            if not run_case(name, function):
                failures += 1
    except Exception as exc:
        failures += 1
        print("FAIL setup/runtime - {}".format(exc))
    finally:
        cleanup_failures = cleanup()

    if cleanup_failures:
        failures += 1
    if failures:
        print("RESULT FAIL - {} case(s) failed".format(failures))
        return 1
    print("RESULT PASS - all user management HTTP cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
