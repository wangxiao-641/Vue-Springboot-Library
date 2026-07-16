package com.example.demo.service;

import com.example.demo.entity.BookWithUser;
import com.example.demo.entity.LendRecord;
import org.springframework.stereotype.Service;

import java.time.Clock;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoUnit;
import java.util.Date;

@Service
public class LoanStatusService {
    public static final ZoneId BUSINESS_ZONE = ZoneId.of("Asia/Shanghai");
    public static final String STATUS_NORMAL = "NORMAL";
    public static final String STATUS_DUE_SOON = "DUE_SOON";
    public static final String STATUS_OVERDUE = "OVERDUE";

    private static final int DUE_SOON_DAYS = 3;
    private static final DateTimeFormatter ADJUSTMENT_FORMAT = DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss");
    private final Clock clock = Clock.system(BUSINESS_ZONE);

    public Date now() {
        return Date.from(clock.instant());
    }

    public Date addCalendarDays(Date date, int days) {
        ZonedDateTime localTime = date.toInstant().atZone(BUSINESS_ZONE);
        return Date.from(localTime.plusDays(days).toInstant());
    }

    public Date startOfToday() {
        return Date.from(LocalDate.now(clock).atStartOfDay(BUSINESS_ZONE).toInstant());
    }

    public boolean isOverdue(Date dueDate) {
        return dueDate != null && dueDate.toInstant().atZone(BUSINESS_ZONE).toLocalDate().isBefore(LocalDate.now(clock));
    }

    public void applyStatus(BookWithUser current) {
        Status status = calculate(current.getDeadtime());
        current.setDueStatus(status.code);
        current.setDueStatusText(status.text);
        current.setOverdueDays(status.overdueDays);
    }

    public void applyStatus(LendRecord record, BookWithUser current) {
        if (current == null || !"0".equals(record.getStatus())) {
            record.setDeadtime(null);
            record.setDueStatus(null);
            record.setDueStatusText(null);
            record.setOverdueDays(0L);
            return;
        }
        applyStatus(current);
        record.setDeadtime(current.getDeadtime());
        record.setDueStatus(current.getDueStatus());
        record.setDueStatusText(current.getDueStatusText());
        record.setOverdueDays(current.getOverdueDays());
    }

    public Date parseAdjustment(String value) {
        if (value == null || value.trim().isEmpty()) {
            throw new CirculationException("应还日期不能为空");
        }
        try {
            LocalDateTime localDateTime = LocalDateTime.parse(value.trim(), ADJUSTMENT_FORMAT);
            return Date.from(localDateTime.atZone(BUSINESS_ZONE).toInstant());
        } catch (DateTimeParseException e) {
            throw new CirculationException("应还日期格式必须为 yyyy-MM-dd HH:mm:ss");
        }
    }

    private Status calculate(Date dueDate) {
        if (dueDate == null) {
            throw new CirculationException("当前借阅缺少应还日期");
        }
        LocalDate today = LocalDate.now(clock);
        LocalDate due = dueDate.toInstant().atZone(BUSINESS_ZONE).toLocalDate();
        long daysUntilDue = ChronoUnit.DAYS.between(today, due);
        if (daysUntilDue < 0) {
            return new Status(STATUS_OVERDUE, "已逾期", -daysUntilDue);
        }
        if (daysUntilDue <= DUE_SOON_DAYS) {
            return new Status(STATUS_DUE_SOON, "即将到期", 0L);
        }
        return new Status(STATUS_NORMAL, "正常", 0L);
    }

    private static class Status {
        private final String code;
        private final String text;
        private final long overdueDays;

        private Status(String code, String text, long overdueDays) {
            this.code = code;
            this.text = text;
            this.overdueDays = overdueDays;
        }
    }
}
