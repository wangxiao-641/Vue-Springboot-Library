#!/usr/bin/env python3
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:9090").rstrip("/")
RUN_ID = str(int(time.time() * 1000))
READER_A_USERNAME = "inv_reader_a_" + RUN_ID
READER_B_USERNAME = "inv_reader_b_" + RUN_ID
BOOK_ISBN = "INV-ISBN-" + RUN_ID
FORGED_BOOK_ISBN = BOOK_ISBN + "-FORGED"
BOOK_NAME = "inventory-test-book-" + RUN_ID

reader_a_id = None
reader_b_id = None
book_id = None


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


def ok(resp):
    return resp.get("code") in ("0", 0)


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def get_records(path, params):
    query = urllib.parse.urlencode(params)
    status, resp = http_json("GET", path + "?" + query)
    if status != 200 or not ok(resp):
        raise AssertionError("query failed: {} {}".format(status, resp))
    return resp.get("data", {}).get("records", [])


def create_reader(username, nick_name):
    status, resp = http_json("POST", "/user/register", {
        "username": username,
        "password": "test123",
        "nickName": nick_name,
        "role": 2,
    })
    assert_true(status == 200 and ok(resp), "create reader failed: {} {}".format(status, resp))
    status, resp = http_json("POST", "/user/login", {
        "username": username,
        "password": "test123",
    })
    assert_true(status == 200 and ok(resp), "login reader failed: {} {}".format(status, resp))
    reader_id = resp.get("data", {}).get("id")
    assert_true(reader_id, "reader id missing: {}".format(resp))
    return reader_id


def setup():
    global reader_a_id, reader_b_id
    reader_a_id = create_reader(READER_A_USERNAME, "Inventory Reader A " + RUN_ID)
    reader_b_id = create_reader(READER_B_USERNAME, "Inventory Reader B " + RUN_ID)


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
    return [
        record for record in get_records("/bookwithuser", {
            "pageNum": 1,
            "pageSize": 50,
            "search1": BOOK_ISBN,
            "search2": "",
            "search3": reader_id or "",
        })
        if record.get("isbn") == BOOK_ISBN and (reader_id is None or record.get("id") == reader_id)
    ]


def lend_records(reader_id=None):
    return [
        record for record in get_records("/LendRecord", {
            "pageNum": 1,
            "pageSize": 100,
            "search1": BOOK_ISBN,
            "search2": "",
            "search3": reader_id or "",
        })
        if record.get("isbn") == BOOK_ISBN and (reader_id is None or record.get("readerId") == reader_id)
    ]


def inventory_snapshot():
    book = find_book()
    return {
        "book": book,
        "current": sorted(current_records(), key=lambda item: (item.get("id"), item.get("isbn"))),
        "lends": sorted(lend_records(), key=lambda item: (item.get("readerId"), item.get("borrownum"))),
    }


def cleanup():
    failures = []
    try:
        for current in current_records():
            _, resp = http_json("POST", "/bookwithuser/deleteRecord", {
                "id": current.get("id"),
                "isbn": current.get("isbn"),
            })
            if not ok(resp):
                failures.append("delete current {}".format(resp))
    except Exception as exc:
        failures.append("query/delete current {}".format(exc))

    try:
        for record in lend_records():
            _, resp = http_json("POST", "/LendRecord/deleteRecord", {
                "isbn": record.get("isbn"),
                "borrownum": record.get("borrownum"),
            })
            if not ok(resp):
                failures.append("delete lend record {}".format(resp))
    except Exception as exc:
        failures.append("query/delete lend records {}".format(exc))

    if book_id:
        _, resp = http_json("DELETE", "/book/{}".format(book_id))
        if not ok(resp):
            failures.append("delete book {}".format(resp))
    try:
        forged_records = get_records("/book", {
            "pageNum": 1,
            "pageSize": 50,
            "search1": FORGED_BOOK_ISBN,
            "search2": "",
            "search3": "",
        })
        for forged in forged_records:
            if forged.get("isbn") == FORGED_BOOK_ISBN:
                _, resp = http_json("DELETE", "/book/{}".format(forged.get("id")))
                if not ok(resp):
                    failures.append("delete forged book {}".format(resp))
    except Exception as exc:
        failures.append("query/delete forged book {}".format(exc))
    for reader_id in (reader_a_id, reader_b_id):
        if reader_id:
            _, resp = http_json("DELETE", "/user/{}".format(reader_id))
            if not ok(resp):
                failures.append("delete reader {}".format(resp))

    try:
        if find_book() is not None:
            failures.append("book still exists after cleanup")
        if current_records():
            failures.append("current borrows still exist after cleanup")
        if lend_records():
            failures.append("lend records still exist after cleanup")
    except Exception as exc:
        failures.append("verify cleanup {}".format(exc))

    if failures:
        print("CLEANUP WARN: " + "; ".join(failures))
    return failures


def run_case(name, func):
    try:
        detail = func()
        print("PASS {} - {}".format(name, detail))
        return True
    except Exception as exc:
        print("FAIL {} - {}".format(name, exc))
        return False


def case_create_total_one_available_one():
    global book_id
    invalid_payloads = [
        ({"isbn": FORGED_BOOK_ISBN, "name": BOOK_NAME + "-missing"}, "missing totalCount"),
        ({"isbn": FORGED_BOOK_ISBN, "name": BOOK_NAME + "-zero", "totalCount": 0}, "zero totalCount"),
        ({"isbn": FORGED_BOOK_ISBN, "name": BOOK_NAME + "-negative", "totalCount": -1}, "negative totalCount"),
        ({"isbn": FORGED_BOOK_ISBN, "name": BOOK_NAME + "-fraction", "totalCount": 1.5}, "fractional totalCount"),
        ({"isbn": FORGED_BOOK_ISBN, "name": BOOK_NAME + "-forged", "totalCount": 1, "availableCount": 99}, "forged availableCount"),
        ({"isbn": FORGED_BOOK_ISBN, "name": BOOK_NAME + "-forged-null", "totalCount": 1, "availableCount": None}, "submitted null availableCount"),
    ]
    for payload, description in invalid_payloads:
        status, resp = http_json("POST", "/book", payload)
        assert_true(status == 200 and not ok(resp), "{} should fail: {}".format(description, resp))

    status, resp = http_json("POST", "/book", {
        "isbn": BOOK_ISBN,
        "name": BOOK_NAME,
        "price": 1,
        "author": "inventory-test",
        "publisher": "inventory-test",
        "borrownum": 0,
        "totalCount": 1,
    })
    assert_true(status == 200 and ok(resp), "create book failed: {} {}".format(status, resp))
    book = find_book()
    assert_true(book, "created book not found")
    book_id = book.get("id")
    assert_true(book.get("totalCount") == 1, "totalCount={}".format(book.get("totalCount")))
    assert_true(book.get("availableCount") == 1, "availableCount={}".format(book.get("availableCount")))
    return "strict positive integer accepted; missing/zero/negative/fraction/availableCount rejected"


def case_reader_a_borrow_stock_zero():
    status, resp = http_json("POST", "/circulation/borrow", {
        "readerId": reader_a_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and ok(resp), "borrow A failed: {}".format(resp))
    book = find_book()
    assert_true(book.get("availableCount") == 0, "availableCount={}".format(book.get("availableCount")))
    assert_true(len(current_records(reader_a_id)) == 1, "reader A current not found")
    assert_true(len([r for r in lend_records(reader_a_id) if r.get("status") == "0"]) == 1, "reader A open lend not found")
    return "reader A borrowed, availableCount=0"


def case_duplicate_batch_delete_rejected_unchanged():
    before = find_book()
    assert_true(before is not None, "book missing before duplicate batch delete")
    status, resp = http_json("POST", "/book/deleteBatch", [book_id, book_id])
    assert_true(status == 200 and not ok(resp), "duplicate batch delete should fail: {}".format(resp))
    assert_true("重复" in str(resp.get("msg", "")), "failure reason is not duplicate id: {}".format(resp))
    after = find_book()
    assert_true(after == before, "book changed or was deleted after duplicate batch request")
    return "duplicate IDs rejected before delete and the book stayed unchanged"


def case_reader_b_borrow_fails_unchanged():
    before = inventory_snapshot()
    status, resp = http_json("POST", "/circulation/borrow", {
        "readerId": reader_b_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and not ok(resp), "borrow B should fail: {}".format(resp))
    after = inventory_snapshot()
    assert_true(after == before, "inventory/current/history changed")
    return "reader B failed at stock 0 and data stayed unchanged"


def case_reader_a_return_stock_one():
    status, resp = http_json("POST", "/circulation/return", {
        "readerId": reader_a_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and ok(resp), "return A failed: {}".format(resp))
    book = find_book()
    assert_true(book.get("availableCount") == 1, "availableCount={}".format(book.get("availableCount")))
    assert_true(len(current_records(reader_a_id)) == 0, "reader A current still exists")
    returned = [record for record in lend_records(reader_a_id) if record.get("status") == "1"]
    assert_true(len(returned) >= 1, "returned lend record not found")
    return "reader A returned, availableCount=1"


def case_update_total_zero_with_borrow_fails_unchanged():
    status, resp = http_json("POST", "/circulation/borrow", {
        "readerId": reader_a_id,
        "isbn": BOOK_ISBN,
    })
    assert_true(status == 200 and ok(resp), "borrow A again failed: {}".format(resp))
    before = inventory_snapshot()
    book = before["book"]
    invalid_updates = [
        ({"id": book.get("id"), "totalCount": 0}, "totalCount=0"),
        ({"id": book.get("id"), "totalCount": -1}, "negative totalCount"),
        ({"id": book.get("id"), "totalCount": 1.5}, "fractional totalCount"),
        ({"id": book.get("id"), "availableCount": 99}, "forged availableCount"),
        ({"id": book.get("id"), "availableCount": None}, "submitted null availableCount"),
        ({"id": book.get("id"), "isbn": BOOK_ISBN + "-CHANGED"}, "ISBN change with active borrow"),
    ]
    for payload, description in invalid_updates:
        status, resp = http_json("PUT", "/book", payload)
        assert_true(status == 200 and not ok(resp), "{} should fail: {}".format(description, resp))
        after = inventory_snapshot()
        assert_true(after == before, "data changed after {}".format(description))
    status, resp = http_json("DELETE", "/book/{}".format(book.get("id")))
    assert_true(status == 200 and not ok(resp), "delete with active borrow should fail: {}".format(resp))
    assert_true(inventory_snapshot() == before, "data changed after delete with active borrow")
    return "invalid stock/ISBN edits and active-loan deletion rejected with data unchanged"


def case_update_total_legal_adjusts_available():
    book = find_book()
    status, resp = http_json("PUT", "/book", {
        "id": book.get("id"),
        "isbn": book.get("isbn"),
        "name": book.get("name"),
        "price": book.get("price"),
        "author": book.get("author"),
        "publisher": book.get("publisher"),
        "createTime": book.get("createTime"),
        "borrownum": book.get("borrownum"),
        "totalCount": 3,
    })
    assert_true(status == 200 and ok(resp), "legal totalCount update failed: {}".format(resp))
    after = find_book()
    assert_true(after.get("totalCount") == 3, "totalCount={}".format(after.get("totalCount")))
    assert_true(after.get("availableCount") == 2, "availableCount={}".format(after.get("availableCount")))
    return "borrowed=1, totalCount=3, availableCount=2"


def case_concurrent_edit_and_duplicate_borrow_are_serialized():
    def borrow_b():
        return http_json("POST", "/circulation/borrow", {
            "readerId": reader_b_id,
            "isbn": BOOK_ISBN,
        })

    def expand_total():
        return http_json("PUT", "/book", {
            "id": book_id,
            "totalCount": 4,
        })

    with ThreadPoolExecutor(max_workers=3) as executor:
        first_borrow = executor.submit(borrow_b)
        second_borrow = executor.submit(borrow_b)
        edit = executor.submit(expand_total)
        responses = [first_borrow.result(), second_borrow.result()]
        edit_status, edit_resp = edit.result()

    successes = [(status, resp) for status, resp in responses if status == 200 and ok(resp)]
    failures = [(status, resp) for status, resp in responses if status == 200 and not ok(resp)]
    assert_true(edit_status == 200 and ok(edit_resp), "concurrent totalCount edit failed: {}".format(edit_resp))
    assert_true(len(successes) == 1, "concurrent successes={} responses={}".format(len(successes), responses))
    assert_true(len(failures) == 1, "concurrent failures={} responses={}".format(len(failures), responses))
    book = find_book()
    assert_true(book.get("totalCount") == 4, "totalCount={}".format(book.get("totalCount")))
    assert_true(book.get("availableCount") == 2, "availableCount={}".format(book.get("availableCount")))
    assert_true(len(current_records()) == 2, "current count={}".format(len(current_records())))
    assert_true(len(current_records(reader_b_id)) == 1, "reader B duplicate current borrow created")
    open_b = [record for record in lend_records(reader_b_id) if record.get("status") == "0"]
    assert_true(len(open_b) == 1, "reader B duplicate open lend created: {}".format(open_b))
    return "edit succeeded; duplicate borrows yielded one success/one failure; total=4 available=2"


def case_refresh_query_still_correct():
    first = find_book()
    second = find_book()
    assert_true(first == second, "repeated query differs")
    assert_true(second.get("totalCount") == 4, "totalCount={}".format(second.get("totalCount")))
    assert_true(second.get("availableCount") == 2, "availableCount={}".format(second.get("availableCount")))
    return "refresh query totalCount=4, availableCount=2"


def main():
    failures = 0
    cleanup_failures = []
    try:
        setup()
        cases = [
            ("create total1 available1", case_create_total_one_available_one),
            ("duplicate batch delete rejected unchanged", case_duplicate_batch_delete_rejected_unchanged),
            ("A borrow then stock0", case_reader_a_borrow_stock_zero),
            ("B borrow fails unchanged", case_reader_b_borrow_fails_unchanged),
            ("A return then stock1", case_reader_a_return_stock_one),
            ("borrowed total0 update fails unchanged", case_update_total_zero_with_borrow_fails_unchanged),
            ("legal total update adjusts available", case_update_total_legal_adjusts_available),
            ("concurrent edit and duplicate borrow serialized", case_concurrent_edit_and_duplicate_borrow_are_serialized),
            ("refresh query still correct", case_refresh_query_still_correct),
        ]
        for name, func in cases:
            if not run_case(name, func):
                failures += 1
    except Exception as exc:
        failures += 1
        print("FAIL setup/runtime - {}".format(exc))
    finally:
        cleanup_failures = cleanup()

    if cleanup_failures:
        failures += 1
        print("FAIL cleanup verification - {} issue(s)".format(len(cleanup_failures)))

    if failures:
        print("RESULT FAIL - {} case(s) failed".format(failures))
        return 1
    print("RESULT PASS - all inventory HTTP cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
