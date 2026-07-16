-- 需求变化4：用户名并发唯一性约束。
-- 脚本可重复执行；如果旧库已有重复用户名，在任何 ALTER 前fail-fast。

DROP PROCEDURE IF EXISTS migrate_user_management;
DELIMITER //
CREATE PROCEDURE migrate_user_management()
BEGIN
  DECLARE username_unique_index_count INT DEFAULT 0;
  DECLARE named_index_column_count INT DEFAULT 0;

  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'user'
      AND column_name = 'username'
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：user 表或 username 字段不存在';
  END IF;

  IF EXISTS (
    SELECT username
    FROM user
    WHERE username IS NOT NULL
    GROUP BY username
    HAVING COUNT(*) > 1
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：user 存在重复用户名，请先清理';
  END IF;

  SELECT COUNT(*) INTO named_index_column_count
  FROM information_schema.statistics
  WHERE table_schema = DATABASE()
    AND table_name = 'user'
    AND index_name = 'uk_user_username';

  IF named_index_column_count > 0 AND (
    named_index_column_count <> 1 OR NOT EXISTS (
      SELECT 1
      FROM information_schema.statistics
      WHERE table_schema = DATABASE()
        AND table_name = 'user'
        AND index_name = 'uk_user_username'
        AND non_unique = 0
        AND column_name = 'username'
        AND seq_in_index = 1
    )
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '迁移中止：uk_user_username 已存在但定义不正确';
  END IF;

  SELECT COUNT(*) INTO username_unique_index_count
  FROM (
    SELECT index_name
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = 'user'
      AND non_unique = 0
    GROUP BY index_name
    HAVING COUNT(*) = 1
       AND MAX(column_name) = 'username'
  ) unique_username_indexes;

  IF username_unique_index_count = 0 THEN
    ALTER TABLE user ADD UNIQUE INDEX uk_user_username (username);
  END IF;
END//
DELIMITER ;

CALL migrate_user_management();
DROP PROCEDURE migrate_user_management;
