-- 需求变化2：当前借阅应还日期完整性与逾期筛选索引。
-- 业务日期以 Asia/Shanghai 自然日计算。
-- 脚本可重复执行；数据校验失败时不执行任何 ALTER。

DROP PROCEDURE IF EXISTS migrate_overdue_management_validate;
DELIMITER //
CREATE PROCEDURE migrate_overdue_management_validate()
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'bookwithuser'
      AND column_name = 'deadtime'
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：bookwithuser 缺少 deadtime 字段';
  END IF;

  IF EXISTS (
    SELECT 1 FROM bookwithuser WHERE deadtime IS NULL
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：bookwithuser 存在 deadtime 为 NULL 的当前借阅，请先纠正应还日期';
  END IF;
END//
DELIMITER ;

CALL migrate_overdue_management_validate();
DROP PROCEDURE migrate_overdue_management_validate;

SET @deadtime_is_nullable = (
  SELECT is_nullable
  FROM information_schema.columns
  WHERE table_schema = DATABASE()
    AND table_name = 'bookwithuser'
    AND column_name = 'deadtime'
);

SET @deadtime_not_null_sql = IF(
  @deadtime_is_nullable = 'YES',
  'ALTER TABLE bookwithuser MODIFY COLUMN deadtime datetime(0) NOT NULL COMMENT ''应归还时间''',
  'SELECT 1'
);

PREPARE overdue_not_null_stmt FROM @deadtime_not_null_sql;
EXECUTE overdue_not_null_stmt;
DEALLOCATE PREPARE overdue_not_null_stmt;

SET @deadtime_index_exists = (
  SELECT COUNT(*)
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'bookwithuser'
    AND index_name = 'idx_bookwithuser_deadtime'
);

SET @deadtime_index_sql = IF(
  @deadtime_index_exists = 0,
  'ALTER TABLE bookwithuser ADD INDEX idx_bookwithuser_deadtime (deadtime)',
  'SELECT 1'
);

PREPARE overdue_index_stmt FROM @deadtime_index_sql;
EXECUTE overdue_index_stmt;
DEALLOCATE PREPARE overdue_index_stmt;
