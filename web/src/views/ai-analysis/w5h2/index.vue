<template>
  <div class="w5h2-analysis-page">
    <!-- 查询表单 -->
    <el-card class="query-panel" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">综合查询</span>
          <span class="field-count">共 {{ fieldConfigs.length }} 个可查询字段</span>
        </div>
      </template>

      <el-form :model="queryForm" label-width="120px" v-loading="loading.init">
        <el-row :gutter="16">
          <!-- 动态渲染所有字段 -->
          <template v-for="field in fieldConfigs" :key="field.field">
            <el-col :span="field.control === 'daterange' ? 12 : 8">
              <el-form-item :label="field.label">
                <!-- 文本输入 -->
                <el-input
                  v-if="field.control === 'input'"
                  v-model="queryForm[field.field]"
                  :placeholder="`请输入${field.label}`"
                  clearable
                />

                <!-- 下拉选择 -->
                <el-select
                  v-else-if="field.control === 'select'"
                  v-model="queryForm[field.field]"
                  :placeholder="`请选择${field.label}`"
                  clearable
                  filterable
                  :multiple="false"
                  @focus="loadFieldOptions(field.field)"
                >
                  <el-option
                    v-for="option in getFieldOptions(field)"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>

                <!-- 日期范围选择 -->
                <el-date-picker
                  v-else-if="field.control === 'daterange'"
                  v-model="queryForm[field.field]"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />

                <!-- 数值输入 -->
                <el-input-number
                  v-else-if="field.control === 'number'"
                  v-model="queryForm[field.field]"
                  :placeholder="`请输入${field.label}`"
                  :controls="false"
                  style="width: 100%"
                />

                <!-- 布尔开关 -->
                <el-switch
                  v-else-if="field.control === 'switch'"
                  v-model="queryForm[field.field]"
                  active-text="是"
                  inactive-text="否"
                />
              </el-form-item>
            </el-col>
          </template>
        </el-row>

        <el-row>
          <el-col :span="24">
            <el-form-item>
              <el-button type="primary" :loading="loading.search" @click="onSearch">
                查询
              </el-button>
              <el-button @click="onReset">重置</el-button>
            </el-form-item>
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
import { reactive, ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import 'github-markdown-css/github-markdown.css'
import * as api from './api'
import type {
  ComplaintItem,
  ComplaintDetail,
  AnalysisSummary,
  FilterCondition,
  FieldConfigItem
} from './types'

// 查询表单（动态字段）
const queryForm = reactive<Record<string, any>>({})

// 字段配置
const fieldConfigs = ref<FieldConfigItem[]>([])

// 字段动态可选值缓存
const fieldOptionsCache = ref<Record<string, Array<{ value: string; label: string }>>>({})

// 加载状态
const loading = reactive({
  search: false,
  detail: false,
  analysis: false,
  exporting: false,
  init: false
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

// 获取字段可选值
const getFieldOptions = (field: FieldConfigItem) => {
  // 如果有固定可选值，返回固定值
  if (field.options && !field.dynamic_options) {
    return field.options
  }

  // 返回缓存的动态可选值
  return fieldOptionsCache.value[field.field] || []
}

// 加载字段动态可选值
const loadFieldOptions = async (fieldName: string) => {
  const field = fieldConfigs.value.find(f => f.field === fieldName)
  if (!field || !field.dynamic_options) return

  // 如果已经加载过，直接返回
  if (fieldOptionsCache.value[fieldName]) return

  try {
    const res = await api.getFieldOptions({ field: fieldName, size: 100 })
    if (res.code === 2000) {
      fieldOptionsCache.value[fieldName] = res.data.options
    }
  } catch (error) {
    console.error('加载字段可选值失败:', error)
  }
}

// 初始化：加载字段配置
const initFieldConfigs = async () => {
  loading.init = true
  try {
    const res = await api.getFieldConfigs()
    if (res.code === 2000) {
      fieldConfigs.value = res.data.fields

      // 初始化queryForm的所有字段
      res.data.fields.forEach(field => {
        if (field.control === 'switch') {
          queryForm[field.field] = undefined
        } else if (field.control === 'daterange') {
          queryForm[field.field] = []
        } else {
          queryForm[field.field] = undefined
        }
      })

      ElMessage.success('初始化成功')
    } else {
      ElMessage.error(res.msg || '初始化失败')
    }
  } catch (error: any) {
    console.error('加载字段配置失败:', error)
    ElMessage.error('初始化失败，请刷新页面重试')
  } finally {
    loading.init = false
  }
}

// 构建查询条件
const buildFilters = (): FilterCondition[] => {
  const filters: FilterCondition[] = []

  fieldConfigs.value.forEach(field => {
    const value = queryForm[field.field]

    // 跳过空值
    if (value === undefined || value === null || value === '') {
      return
    }

    // 跳过空数组
    if (Array.isArray(value) && value.length === 0) {
      return
    }

    // 根据字段类型和控件确定操作符
    let operator = field.operators[0] // 默认使用第一个操作符
    let filterValue = value

    // 日期范围特殊处理
    if (field.control === 'daterange' && Array.isArray(value) && value.length === 2) {
      operator = 'range'
      filterValue = value
    }
    // 下拉选择默认使用eq
    else if (field.control === 'select') {
      operator = 'eq'
    }
    // 文本输入默认使用like
    else if (field.control === 'input' && field.es_type === 'text') {
      operator = 'like'
    }
    // 数值和关键词默认使用eq
    else if (field.control === 'input' || field.control === 'number') {
      operator = 'eq'
    }

    filters.push({
      field: field.field,
      operator: operator,
      value: filterValue
    })
  })

  return filters
}

// 查询
const onSearch = async () => {
  const filters = buildFilters()

  if (filters.length === 0) {
    ElMessage.warning('请至少填写一个查询条件')
    return
  }

  pagination.page = 1
  await loadData(filters)
}

// 重置
const onReset = () => {
  // 重置所有表单字段
  fieldConfigs.value.forEach(field => {
    if (field.control === 'switch') {
      queryForm[field.field] = undefined
    } else if (field.control === 'daterange') {
      queryForm[field.field] = []
    } else {
      queryForm[field.field] = undefined
    }
  })

  pagination.page = 1
  pagination.total = 0
  tableData.value = []
  analysisReport.value = ''
  analysisSummary.value = null
}

// 分页变化
const onPageChange = (page: number) => {
  pagination.page = page
  const filters = buildFilters()
  loadData(filters)
}

// 加载数据
const loadData = async (filters: FilterCondition[]) => {
  loading.search = true
  analysisReport.value = ''
  analysisSummary.value = null

  try {
    const params = {
      filters: filters,
      logic: 'AND' as 'AND',
      page: pagination.page,
      size: pagination.pageSize,
      sort_field: 'accept_time',
      sort_order: 'desc' as 'desc'
    }

    const res = await api.comprehensiveSearch(params)
    if (res.code === 2000) {
      // 转换数据格式以适配表格
      const rawData = res.data.data || []
      tableData.value = rawData.map(item => ({
        serial_number: item.id || '',
        title: item.title || '',
        content: item.content || '',
        time: item.accept_time || '',
        region: item.region || '',
        status: item.status || '',
        type: item.complaint_type || ''
      }))
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

  ElMessage.info('大模型分析功能开发中...')
  // TODO: 基于综合查询条件生成分析报告
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

onMounted(async () => {
  // 页面加载时初始化字段配置
  await initFieldConfigs()
})
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

      .field-count {
        font-size: 14px;
        color: #909399;
        margin-left: 12px;
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
