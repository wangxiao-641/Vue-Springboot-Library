# 变更模板：新增数据库表

## 前置检查

- [ ] 确认表名不与现有表冲突（现有表：`user`, `book`, `lend_record`, `bookwithuser`）
- [ ] 确认字段命名使用下划线小写（如 `create_time`），Entity 中自动映射为驼峰
- [ ] 确认是否需要关联外键，外键字段命名：被关联表名 + `_id`（如 `reader_id`）

## 改动清单（按顺序执行）

### 1. 编写建表 SQL

创建表后追加到 `sql/springboot-vue.sql` 末尾：

```sql
-- ----------------------------
-- Table structure for xxx
-- ----------------------------
DROP TABLE IF EXISTS `xxx`;
CREATE TABLE `xxx` (
  `id` bigint(0) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '名称',
  `create_time` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'xxx表' ROW_FORMAT = Dynamic;
```

**注意事项**：
- 所有表用 InnoDB 引擎
- 字符集 `utf8mb4`，排序规则 `utf8mb4_unicode_ci`
- 主键 `id` 用 `bigint AUTO_INCREMENT`
- 日期类型用 `datetime(0)`，不要用 `timestamp`（2038 问题）
- status 字段用 `varchar(1)`，0/1 表示状态
- 价格用 `decimal(10, 2)`

### 2. Application 中执行 SQL

如果 Docker 已运行，可以直接在 MySQL 中执行新表：

```bash
docker exec library-mysql mysql -u root -pAb50858553 springboot-vue -e "
  CREATE TABLE IF NOT EXISTS xxx (
    id BIGINT NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"
```

Docker 重新启动时会自动执行 `sql/springboot-vue.sql` 中的建表语句。

### 3. Entity 实体类

在 `SpringBoot/src/main/java/com/example/demo/entity/` 下新建：

```java
package com.example.demo.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import java.util.Date;

@Data
@TableName("xxx")
public class Xxx {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String name;

    @JsonFormat(locale = "zh", timezone = "GMT+8", pattern = "yyyy-MM-dd")
    private Date createTime;
}
```

**检查清单**：
- [ ] `@Data` 注解（Lombok 自动生成 getter/setter）
- [ ] `@TableName` 值与表名一致
- [ ] 主键字段加 `@TableId(type = IdType.AUTO)`
- [ ] 日期字段加 `@JsonFormat` 注解
- [ ] Java 类型对应：`Long`↔`bigint`、`String`↔`varchar`、`Date`↔`datetime`、`BigDecimal`↔`decimal`

### 4. Mapper 接口

在 `SpringBoot/src/main/java/com/example/demo/mapper/` 下新建：

```java
package com.example.demo.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.demo.entity.Xxx;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface XxxMapper extends BaseMapper<Xxx> {
}
```

### 5. 编译验证

```bash
cd SpringBoot && mvn package -DskipTests -q 2>&1 | tail -5
# 期望: BUILD SUCCESS
```

### 6. 上下文文档更新

- [ ] 在 `library-context.md` 的数据库表格章节添加新表信息
- [ ] 在 Entity 文件清单中补充新文件
- [ ] 在 Mapper 文件清单中补充新文件
