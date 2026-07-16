-- 需求变化1：支持图书库存数量，并修正当前借阅约束。
-- 适用基线：book 已有 total_count / available_count，bookwithuser 仍以 book_name 为主键。
-- 本脚本先做强制前置校验；任何不安全数据或非预期表结构都会 SIGNAL 中止，
-- 不会出现“检查查询有结果但 ALTER 仍继续执行”的部分迁移。

DROP PROCEDURE IF EXISTS migrate_inventory_counts_validate;
DELIMITER //
CREATE PROCEDURE migrate_inventory_counts_validate()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'book' AND column_name = 'total_count'
  ) OR NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'book' AND column_name = 'available_count'
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：book 缺少 total_count/available_count，请先升级到适用基线';
  END IF;

  IF EXISTS (
    SELECT isbn FROM book GROUP BY isbn HAVING COUNT(*) > 1
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：book 存在重复 ISBN，请先清理';
  END IF;

  IF EXISTS (
    SELECT id, isbn FROM bookwithuser GROUP BY id, isbn HAVING COUNT(*) > 1
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：bookwithuser 存在同一读者重复 ISBN，请先清理';
  END IF;

  IF EXISTS (
    SELECT 1 FROM book
    WHERE total_count IS NULL
       OR available_count IS NULL
       OR total_count <= 0
       OR available_count < 0
       OR available_count > total_count
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：book 存在非法库存数量，请先清理';
  END IF;

  IF EXISTS (
    SELECT 1 FROM bookwithuser WHERE isbn IS NULL OR TRIM(isbn) = ''
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：bookwithuser 存在空 ISBN，请先清理';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM bookwithuser current_borrow
    LEFT JOIN book b ON b.isbn = current_borrow.isbn
    WHERE b.id IS NULL
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：bookwithuser 存在找不到图书的 ISBN，请先清理';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM book b
    LEFT JOIN (
      SELECT isbn, COUNT(*) AS borrowed_count
      FROM bookwithuser
      GROUP BY isbn
    ) current_count ON current_count.isbn = b.isbn
    WHERE COALESCE(current_count.borrowed_count, 0) > b.total_count
       OR b.available_count <> b.total_count - COALESCE(current_count.borrowed_count, 0)
       OR b.status <> IF(b.available_count > 0, '1', '0')
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：库存数量/status 与当前借阅不一致，请先修复';
  END IF;

  IF EXISTS (
    SELECT 1
    FROM bookwithuser current_borrow
    LEFT JOIN (
      SELECT reader_id, isbn, COUNT(*) AS open_count
      FROM lend_record
      WHERE status = '0'
      GROUP BY reader_id, isbn
    ) open_lend
      ON open_lend.reader_id = current_borrow.id
     AND open_lend.isbn = current_borrow.isbn
    WHERE COALESCE(open_lend.open_count, 0) <> 1
  ) OR EXISTS (
    SELECT 1
    FROM lend_record open_lend
    LEFT JOIN bookwithuser current_borrow
      ON current_borrow.id = open_lend.reader_id
     AND current_borrow.isbn = open_lend.isbn
    WHERE open_lend.status = '0' AND current_borrow.id IS NULL
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：当前借阅与未归还记录不一致，请先修复';
  END IF;

  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'bookwithuser' AND column_name = 'borrow_id'
  ) OR EXISTS (
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'book' AND index_name = 'uk_book_isbn'
  ) OR EXISTS (
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'bookwithuser' AND index_name = 'uk_bookwithuser_reader_isbn'
  ) OR EXISTS (
    SELECT 1 FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'bookwithuser' AND index_name = 'idx_bookwithuser_isbn'
  ) OR EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE constraint_schema = DATABASE()
      AND table_name = 'book'
      AND constraint_name IN ('chk_book_total_count_positive', 'chk_book_available_count_range')
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：检测到已迁移或部分迁移结构，请勿重复执行并先核对表结构';
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_schema = kcu.constraint_schema
     AND tc.table_name = kcu.table_name
     AND tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_schema = DATABASE()
      AND tc.table_name = 'bookwithuser'
      AND tc.constraint_type = 'PRIMARY KEY'
      AND kcu.column_name = 'book_name'
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：bookwithuser 主键不是预期的 book_name，请先核对基线';
  END IF;
END//
DELIMITER ;

CALL migrate_inventory_counts_validate();
DROP PROCEDURE migrate_inventory_counts_validate;

ALTER TABLE book
  ADD UNIQUE INDEX uk_book_isbn (isbn),
  ADD CONSTRAINT chk_book_total_count_positive CHECK (total_count > 0),
  ADD CONSTRAINT chk_book_available_count_range CHECK (available_count >= 0 AND available_count <= total_count);

ALTER TABLE bookwithuser
  DROP PRIMARY KEY,
  ADD COLUMN borrow_id BIGINT NOT NULL AUTO_INCREMENT FIRST,
  MODIFY isbn VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '图书编号',
  ADD PRIMARY KEY (borrow_id),
  ADD UNIQUE INDEX uk_bookwithuser_reader_isbn (id, isbn),
  ADD INDEX idx_bookwithuser_isbn (isbn);
