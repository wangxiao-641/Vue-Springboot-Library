<template>
  <div class="page-shell">
    <PageHeader
      title="运营概览"
      description="快速掌握馆藏流通、访问与读者规模。"
    >
      <template #actions
        ><div class="date-chip">
          <el-icon><Calendar /></el-icon
          ><span id="myTimer">{{ currentTime }}</span>
        </div></template
      >
    </PageHeader>
    <div class="metric-grid">
      <div
        v-for="item in cards"
        :key="item.title"
        class="surface-card metric-card"
      >
        <div class="metric-label">{{ item.title }}</div>
        <div class="metric-value">{{ item.data }}</div>
        <el-icon class="metric-icon"
          ><component :is="item.component"
        /></el-icon>
      </div>
    </div>
    <div class="surface-card chart-card">
      <div class="chart-heading">
        <div>
          <div class="chart-title">馆藏运营数据</div>
          <div class="muted">当前系统关键指标对比</div>
        </div>
        <el-tag type="success" effect="plain">实时数据</el-tag>
      </div>
      <div id="main" />
    </div>
  </div>
</template>
<script>
import * as echarts from "echarts";
import { ElMessage } from "element-plus";
import request from "../utils/request";
import PageHeader from "../components/PageHeader";
export default {
  components: { PageHeader },
  data() {
    return {
      timer: null,
      chart: null,
      currentTime: "",
      cards: [
        { title: "借阅记录", data: "—", component: "Tickets" },
        { title: "累计访问", data: "—", component: "View" },
        { title: "馆藏图书", data: "—", component: "Collection" },
        { title: "注册用户", data: "—", component: "UserFilled" },
      ],
    };
  },
  mounted() {
    this.updateTimer();
    this.timer = setInterval(this.updateTimer, 1000);
    request.get("/dashboard").then((res) => {
      if (res.code == 0) {
        this.cards[0].data = res.data.lendRecordCount;
        this.cards[1].data = res.data.visitCount;
        this.cards[2].data = res.data.bookCount;
        this.cards[3].data = res.data.userCount;
        this.renderChart();
      } else ElMessage.error(res.msg);
    });
    window.addEventListener("resize", this.resizeChart);
  },
  beforeUnmount() {
    clearInterval(this.timer);
    window.removeEventListener("resize", this.resizeChart);
    if (this.chart) this.chart.dispose();
  },
  methods: {
    updateTimer() {
      this.currentTime = new Date().toLocaleString("zh-CN", { hour12: false });
    },
    resizeChart() {
      if (this.chart) this.chart.resize();
    },
    renderChart() {
      this.chart = echarts.init(document.getElementById("main"));
      this.chart.setOption({
        color: ["#0f766e"],
        tooltip: { trigger: "axis" },
        grid: { left: 20, right: 20, top: 35, bottom: 15, containLabel: true },
        xAxis: {
          type: "category",
          data: this.cards.map((i) => i.title),
          axisLine: { lineStyle: { color: "#d9e2ec" } },
          axisTick: { show: false },
          axisLabel: { color: "#486581" },
        },
        yAxis: {
          type: "value",
          splitLine: { lineStyle: { color: "#edf2f7" } },
          axisLabel: { color: "#829ab1" },
        },
        series: [
          {
            type: "bar",
            barMaxWidth: 54,
            data: this.cards.map((i, n) => ({
              value: i.data,
              itemStyle: {
                color: ["#0f766e", "#2f80a3", "#d28b35", "#6b63a8"][n],
                borderRadius: [7, 7, 0, 0],
              },
            })),
            label: {
              show: true,
              position: "top",
              color: "#243b53",
              fontWeight: 700,
            },
          },
        ],
      });
    },
  },
};
</script>
<style scoped>
.date-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border: 1px solid var(--line);
  border-radius: 9px;
  color: var(--ink-600);
  background: #fff;
  font-size: 13px;
}
.date-chip .el-icon {
  color: var(--accent);
}
#main {
  width: 100%;
  height: 410px;
}
</style>
