<template>
  <div class="w5h2-analysis-page">
    <!-- 查询表单 -->
    <el-card class="query-panel" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">5W2H 诉求分析</span>
        </div>
      </template>

      <el-form :model="queryForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="queryForm.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="地区">
              <el-select
                v-model="queryForm.region"
                clearable
                placeholder="请选择地区"
                style="width: 100%"
              >
                <el-option
                  v-for="item in regionOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="关键词">
              <el-input
                v-model="queryForm.keywords"
                clearable
                placeholder="请输入关键词"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="工单编号">
              <el-input
                v-model="queryForm.serialNumber"
                clearable
                placeholder="请输入工单编号"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="诉求类型">
              <el-select
                v-model="queryForm.type"
                clearable
                placeholder="请选择诉求类型"
                style="width: 100%"
              >
                <el-option
                  v-for="item in typeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12" style="text-align: right">
            <el-button type="primary" :loading="loading.search" @click="onSearch">
              查询
            </el-button>
            <el-button @click="onReset">重置</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-panel" shadow="never">
      <template #header>
        <div class="panel-header">
          <div class="panel-title">
            <h2>查询结果</h2>
            <span class="panel-subtitle">共 {{ pagination.total }} 条记录</span>
          </div>
          <div class="panel-actions">
            <el-button
              type="primary"
              :loading="loading.analysis"
              :disabled="pagination.total === 0"
              @click="onAnalyze"
            >
              大模型分析
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="tableData"
        border
        stripe
        v-loading="loading.search"
        height="400"
      >
        <el-table-column prop="serial_number" label="工单编号" width="160" />
        <el-table-column prop="title" label="诉求标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="content" label="诉求内容" min-width="260" show-overflow-tooltip />
        <el-table-column prop="time" label="诉求时间" width="160" />
        <el-table-column prop="region" label="地区" width="120" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="text" @click="openDetail(row.serial_number)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next, jumper"
          @current-change="onPageChange"
        />
      </div>
    </el-card>

    <!-- 大模型分析报告 -->
    <el-card
      v-if="analysisReport"
      ref="analysisSectionRef"
      class="analysis-panel"
      shadow="never"
    >
      <template #header>
        <div class="panel-header">
          <div class="panel-title">
            <h2>大模型分析报告</h2>
            <span class="panel-subtitle">基于当前查询结果自动生成</span>
          </div>
          <div class="panel-actions">
            <el-button
              type="primary"
              plain
              :loading="loading.exporting"
              @click="onExportReport"
            >
              导出 Word
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="analysisSummary" class="analysis-meta">
        <p>
          总记录数：{{ analysisSummary.total ?? pagination.total }}
          <span v-if="analysisSummary.time_range?.start && analysisSummary.time_range?.end">
            ｜ 时间范围：{{ analysisSummary.time_range.start }} ~ {{ analysisSummary.time_range.end }}
          </span>
        </p>
        <p v-if="analysisSummary.top_categories?.length">
          热门分类：
          <span class="analysis-emphasis">
            {{ analysisSummary.top_categories.map((item) => `${item.label}·${item.count}条`).join('，') }}
          </span>
        </p>
        <p v-if="analysisSummary.top_regions?.length">
          高频区域：
          <span class="analysis-emphasis">
            {{ analysisSummary.top_regions.map((item) => `${item.label}·${item.count}条`).join('，') }}
          </span>
        </p>
      </div>

      <div class="analysis-markdown" v-html="analysisHtml"></div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="诉求详情"
      width="80%"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-if="loading.detail" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="currentDetail" class="detail-container">
        <el-descriptions :column="2" border>
          <!-- 基本信息 -->
          <el-descriptions-item label="工单编号">{{ currentDetail.serial_number }}</el-descriptions-item>
          <el-descriptions-item label="诉求时间">{{ currentDetail.request_time }}</el-descriptions-item>
          <el-descriptions-item label="诉求类型">{{ currentDetail.type }}</el-descriptions-item>
          <el-descriptions-item label="诉求来源">{{ currentDetail.source }}</el-descriptions-item>
          <el-descriptions-item label="诉求标题" :span="2">{{ currentDetail.title }}</el-descriptions-item>
          <el-descriptions-item label="诉求内容" :span="2">
            <div class="content-text">{{ currentDetail.content }}</div>
          </el-descriptions-item>

          <!-- 联系信息 -->
          <el-descriptions-item label="联系电话">{{ currentDetail.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系人">{{ currentDetail.contact || '-' }}</el-descriptions-item>

          <!-- 地址信息 -->
          <el-descriptions-item label="诉求地区">{{ currentDetail.region }}</el-descriptions-item>
          <el-descriptions-item label="详细地址">{{ currentDetail.address || '-' }}</el-descriptions-item>

          <!-- 处理信息 -->
          <el-descriptions-item label="办理部门">{{ currentDetail.department || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工单状态">{{ currentDetail.status }}</el-descriptions-item>
          <el-descriptions-item label="处理方式">{{ currentDetail.handle_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ currentDetail.category || '-' }}</el-descriptions-item>

          <!-- 时间线 -->
          <el-descriptions-item label="登记时间">{{ currentDetail.register_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ currentDetail.finish_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="答复时间">{{ currentDetail.answer_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">{{ currentDetail.risk_level || '-' }}</el-descriptions-item>

          <!-- 答复内容 -->
          <el-descriptions-item label="答复内容" :span="2">
            <div class="content-text">{{ currentDetail.answer_content || '-' }}</div>
          </el-descriptions-item>

          <!-- 评价 -->
          <el-descriptions-item label="满意度">{{ currentDetail.satisfaction || '-' }}</el-descriptions-item>
          <el-descriptions-item label="评分">{{ currentDetail.rating || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="w5h2Analysis">
import { reactive, ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import 'github-markdown-css/github-markdown.css'
import * as api from './api'
import type { ComplaintItem, ComplaintDetail, AnalysisSummary } from './types'
import { dictionary } from '/@/utils/dictionary'

// 查询表单
const queryForm = reactive({
  dateRange: [] as string[],
  region: '',
  keywords: '',
  serialNumber: '',
  type: ''
})

// 加载状态
const loading = reactive({
  search: false,
  detail: false,
  analysis: false,
  exporting: false
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 表格数据
const tableData = ref<ComplaintItem[]>([])

// 详情弹窗
const detailVisible = ref(false)
const currentDetail = ref<ComplaintDetail | null>(null)

// 大模型分析
const analysisReport = ref('')
const analysisSummary = ref<AnalysisSummary | null>(null)
const analysisSectionRef = ref<any>(null)

// 字典选项
const regionOptions = computed(() => dictionary('region') || [])
const typeOptions = computed(() => dictionary('complaint_type') || [])

// Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

// Markdown 渲染
const analysisHtml = computed(() =>
  analysisReport.value ? md.render(analysisReport.value) : ''
)

// 查询
const onSearch = async () => {
  pagination.page = 1
  await loadData()
}

// 重置
const onReset = () => {
  queryForm.dateRange = []
  queryForm.region = ''
  queryForm.keywords = ''
  queryForm.serialNumber = ''
  queryForm.type = ''
  pagination.page = 1
  pagination.total = 0
  tableData.value = []
  analysisReport.value = ''
  analysisSummary.value = null
}

// 分页变化
const onPageChange = (page: number) => {
  pagination.page = page
  loadData()
}

// 加载数据
const loadData = async () => {
  loading.search = true
  analysisReport.value = ''
  analysisSummary.value = null

  try {
    const params: any = {
      page: pagination.page,
      size: pagination.pageSize
    }

    if (queryForm.dateRange && queryForm.dateRange.length === 2) {
      params.start_time = queryForm.dateRange[0]
      params.end_time = queryForm.dateRange[1]
    }
    if (queryForm.region) {
      params.region = queryForm.region
    }
    if (queryForm.keywords) {
      params.keywords = queryForm.keywords
    }
    if (queryForm.serialNumber) {
      params.serial_number = queryForm.serialNumber
    }
    if (queryForm.type) {
      params.type = queryForm.type
    }

    const res = await api.searchComplaints(params)
    if (res.code === 2000) {
      tableData.value = res.data.data || []
      pagination.total = res.data.total || 0
      ElMessage.success(`查询成功，共 ${pagination.total} 条记录`)
    } else {
      ElMessage.error(res.msg || '查询失败')
    }
  } catch (error: any) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请重试')
  } finally {
    loading.search = false
  }
}

// 查看详情
const openDetail = async (serialNumber: string) => {
  detailVisible.value = true
  loading.detail = true
  currentDetail.value = null

  try {
    const res = await api.getComplaintDetail(serialNumber)
    if (res.code === 2000) {
      currentDetail.value = res.data
    } else {
      ElMessage.error(res.msg || '获取详情失败')
      detailVisible.value = false
    }
  } catch (error: any) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败，请重试')
    detailVisible.value = false
  } finally {
    loading.detail = false
  }
}

// 大模型分析
const onAnalyze = async () => {
  if (pagination.total === 0) {
    ElMessage.warning('请先执行查询后再进行分析')
    return
  }

  loading.analysis = true

  try {
    const params: any = {}

    if (queryForm.dateRange && queryForm.dateRange.length === 2) {
      params.start_time = queryForm.dateRange[0]
      params.end_time = queryForm.dateRange[1]
    }
    if (queryForm.region) {
      params.region = queryForm.region
    }
    if (queryForm.keywords) {
      params.keywords = queryForm.keywords
    }
    if (queryForm.serialNumber) {
      params.serial_number = queryForm.serialNumber
    }
    if (queryForm.type) {
      params.type = queryForm.type
    }

    const res = await api.analyzeComplaints(params)
    if (res.code === 2000) {
      analysisReport.value = res.data.analysis
      analysisSummary.value = res.data.summary
      ElMessage.success('分析报告生成成功')

      await nextTick()
      analysisSectionRef.value?.$el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    } else {
      ElMessage.error(res.msg || '分析失败')
    }
  } catch (error: any) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败，请重试')
  } finally {
    loading.analysis = false
  }
}

// 导出报告
const onExportReport = async () => {
  if (!analysisReport.value || !analysisSummary.value) {
    ElMessage.warning('请先生成分析报告')
    return
  }

  loading.exporting = true
  try {
    const blob = await api.exportReport({
      analysis: analysisReport.value,
      summary: analysisSummary.value
    })

    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    link.href = url
    link.download = `5W2H分析报告_${timestamp}.docx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('报告导出成功')
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    loading.exporting = false
  }
}
</script>

<style scoped lang="scss">
.w5h2-analysis-page {
  padding: 16px;

  .query-panel,
  .table-panel,
  .analysis-panel {
    margin-bottom: 16px;

    .card-header,
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .card-title,
      .panel-title h2 {
        font-weight: 600;
        font-size: 16px;
      }

      .panel-title {
        display: flex;
        align-items: baseline;
        gap: 12px;

        h2 {
          font-size: 20px;
          color: #1f1f1f;
          margin: 0;
        }

        .panel-subtitle {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }

  .analysis-meta {
    font-size: 14px;
    color: #606266;
    line-height: 1.6;
    margin-bottom: 16px;

    .analysis-emphasis {
      font-weight: 600;
      color: #303133;
    }
  }

  .analysis-markdown {
    background: #f6f8fa;
    border-radius: 8px;
    padding: 16px;
    font-size: 14px;
    line-height: 1.7;
    color: #1f2933;
    overflow-x: auto;

    :deep(h1),
    :deep(h2),
    :deep(h3) {
      margin: 16px 0 8px;
      font-weight: 600;
      color: #1f2933;
    }

    :deep(p),
    :deep(li) {
      margin: 8px 0;
      line-height: 1.8;
    }

    :deep(ul) {
      padding-left: 20px;
    }
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 0;
    color: #909399;

    .el-icon {
      font-size: 32px;
      margin-bottom: 12px;
    }
  }

  .detail-container {
    max-height: 70vh;
    overflow-y: auto;
  }

  .content-text {
    white-space: pre-wrap;
    line-height: 1.6;
    max-height: 300px;
    overflow-y: auto;
  }
}
</style>
