<template>
  <div class="thematic-analysis-page">
    <!-- 顶部：专题输入 + 操作按钮 -->
    <el-card class="top-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="card-title">AI 专题分析</span>
        </div>
      </template>

      <el-row :gutter="12">
        <el-col :span="24">
          <el-input
            v-model="state.topic"
            placeholder="请输入专题问题，例如：道路积水"
            clearable
            size="large"
            @keyup.enter="onDescribe"
          />
        </el-col>
      </el-row>

      <el-row :gutter="12" style="margin-top: 12px">
        <el-col :span="24">
          <el-space wrap>
            <el-button type="primary" :loading="loading.describe" @click="onDescribe">
              概要描述
            </el-button>
            <el-button :loading="loading.keywords" @click="onExtractKeywords">
              特征提取
            </el-button>
            <el-button :loading="loading.list" :disabled="!canFetchList" @click="onFetchList">
              获取问题清单
            </el-button>
            <el-button :loading="loading.analysis" :disabled="!canAnalyze" @click="onSmartAnalyze">
              智能分析
            </el-button>
            <el-button type="success" :loading="loading.exporting" @click="onExportReport">
              导出报告
            </el-button>
          </el-space>
        </el-col>
      </el-row>
    </el-card>

    <!-- 概要描述 -->
    <el-card class="section-card" shadow="never" v-loading="loading.describe">
      <template #header>
        <div class="card-header">
          <span class="card-title">概要描述</span>
        </div>
      </template>

      <div class="summary-content" v-if="state.summary" v-html="formatTextWithBreaks(state.summary)"></div>
      <el-empty v-else description="点击上方【概要描述】按钮以生成内容" />
    </el-card>

    <!-- 特征关键词 -->
    <el-card class="section-card" shadow="never" v-loading="loading.keywords">
      <template #header>
        <div class="card-header">
          <span class="card-title">特征关键词</span>
        </div>
      </template>

      <div class="keyword-section" v-if="state.keywords.length > 0">
        <div class="keyword-list">
          <el-tag
            class="keyword-tag"
            size="large"
            :type="allSelected ? 'primary' : ''"
            @click="toggleAll"
          >
            全部
          </el-tag>

          <template v-for="(kw, idx) in state.keywords" :key="idx">
            <el-tag
              v-if="editingIndex !== idx"
              class="keyword-tag"
              size="large"
              :type="filters.keywords.includes(kw) ? 'primary' : ''"
              closable
              @click="toggleKeyword(kw)"
              @dblclick="startEdit(idx)"
              @close="removeKeyword(kw)"
            >
              {{ kw }}
            </el-tag>
            <el-input
              v-else
              v-model="editingValue"
              size="small"
              maxlength="16"
              show-word-limit
              style="width: 120px"
              @keyup.enter="confirmEdit"
              @blur="confirmEdit"
            />
          </template>
        </div>

        <div class="keyword-actions">
          <el-input
            v-model="keywordInput"
            placeholder="输入关键词后回车"
            clearable
            size="small"
            maxlength="16"
            show-word-limit
            style="width: 200px"
            @keyup.enter="addKeyword"
          />
          <el-button size="small" @click="addKeyword">添加</el-button>
        </div>
      </div>
      <el-empty v-else description="点击上方【特征提取】按钮以生成关键词" />
    </el-card>

    <!-- 问题清单 -->
    <el-card class="section-card" shadow="never" v-loading="loading.list" v-if="state.hasFetchedList">
      <template #header>
        <div class="card-header">
          <span class="card-title">问题清单</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :model="filters" label-width="90px" class="filter-form">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="关键词">
              <el-select
                v-model="filters.keywords"
                multiple
                filterable
                clearable
                placeholder="选择或输入关键词"
                style="width: 100%"
              >
                <el-option
                  v-for="kw in state.keywords"
                  :key="kw"
                  :label="kw"
                  :value="kw"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="地区">
              <el-select
                v-model="filters.region"
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

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="filters.dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12" style="text-align: right">
            <el-button type="primary" @click="applyFilters">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-col>
        </el-row>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="currentList" border stripe v-if="currentList.length > 0">
        <el-table-column prop="serial_number" label="诉求编号" width="160" />
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="content" label="内容摘要" min-width="320" show-overflow-tooltip />
        <el-table-column prop="time" label="时间" width="160" />
        <el-table-column prop="handling_area" label="处理地区" width="140" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="text" @click="openDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="请设置筛选条件并点击查询按钮获取数据" />

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="currentList.length > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          layout="total, prev, pager, next, jumper"
          @current-change="onPageChange"
        />
      </div>
    </el-card>

    <!-- 智能分析 -->
    <el-card class="section-card" shadow="never" v-loading="loading.analysis" v-if="state.hasFetchedList">
      <template #header>
        <div class="card-header">
          <span class="card-title">智能分析</span>
        </div>
      </template>

      <div class="markdown-body" v-if="state.analysisMarkdown" v-html="md.render(state.analysisMarkdown)"></div>
      <el-empty v-else description="点击上方【智能分析】按钮以生成内容" />
    </el-card>

    <!-- 工单详情组件 -->
    <ComplaintDetail ref="complaintDetailRef" />
  </div>
</template>

<script setup lang="ts" name="thematicAnalysis">
import { reactive, computed, ref, defineAsyncComponent } from 'vue'
import { ElMessage } from 'element-plus'
import * as api from './api'
import type { ComplaintItem } from './types'
import { dictionary } from '/@/utils/dictionary'
import MarkdownIt from 'markdown-it'
import 'github-markdown-css/github-markdown.css'

// 工单详情组件
const ComplaintDetail = defineAsyncComponent(() =>
  import('/@/components/ComplaintDetail/index.vue')
)
const complaintDetailRef = ref()

// 页面状态
const state = reactive({
  topic: '',
  summary: '',
  keywords: [] as string[],
  analysisMarkdown: '',
  hasExtractedFeatures: false,
  hasFetchedList: false,
  currentReportId: ''
})

// 加载状态
const loading = reactive({
  describe: false,
  keywords: false,
  list: false,
  analysis: false,
  exporting: false
})

// 关键词编辑
const keywordInput = ref('')
const editingIndex = ref<number | null>(null)
const editingValue = ref('')

// 筛选条件
const filters = reactive({
  keywords: [] as string[],
  dateRange: [] as string[],
  region: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 当前列表数据
const currentList = ref<ComplaintItem[]>([])

// Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

// 地区选项（从系统字典获取）
const regionOptions = computed(() => dictionary('region') || [])

// 按钮可用状态
const canFetchList = computed(() => state.hasExtractedFeatures)
const canAnalyze = computed(() => state.hasFetchedList)

// 全选状态
const allSelected = computed(() => {
  return state.keywords.length > 0 && filters.keywords.length === state.keywords.length
})

// 格式化文本（换行符转<br>）
const formatTextWithBreaks = (text: string) => {
  return text.replace(/\n/g, '<br>')
}

// 1. 概要描述
const onDescribe = async () => {
  if (!state.topic.trim()) {
    ElMessage.warning('请先输入专题问题')
    return
  }

  loading.describe = true
  try {
    const res = await api.DescribeProblem({ title: state.topic.trim() })
    if (res.code === 2000) {
      state.summary = res.data.explanation
      ElMessage.success('概要描述生成成功')
    } else {
      ElMessage.error(res.msg || '概要描述生成失败')
    }
  } catch (error: any) {
    console.error('概要描述失败:', error)
    ElMessage.error('概要描述生成失败，请重试')
  } finally {
    loading.describe = false
  }
}

// 2. 特征提取
const onExtractKeywords = async () => {
  if (!state.topic.trim()) {
    ElMessage.warning('请先输入专题问题')
    return
  }

  // 重置后续流程
  state.hasExtractedFeatures = false
  state.hasFetchedList = false
  state.analysisMarkdown = ''

  loading.keywords = true
  try {
    const res = await api.ExtractKeywords({ title: state.topic.trim() })
    if (res.code === 2000) {
      state.keywords = res.data.keywords || []
      filters.keywords = [...state.keywords]
      state.hasExtractedFeatures = true
      ElMessage.success(`成功提取 ${state.keywords.length} 个关键词`)
    } else {
      ElMessage.error(res.msg || '关键词提取失败')
    }
  } catch (error: any) {
    console.error('关键词提取失败:', error)
    ElMessage.error('关键词提取失败，请重试')
  } finally {
    loading.keywords = false
  }
}

// 3. 获取问题清单
const onFetchList = async () => {
  if (!filters.keywords || filters.keywords.length === 0) {
    ElMessage.warning('请至少选择一个关键词')
    return
  }

  loading.list = true
  try {
    const params: any = {
      keywords: filters.keywords,
      page: pagination.page,
      size: pagination.pageSize
    }

    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = filters.dateRange[0]
      params.end_time = filters.dateRange[1]
    }
    if (filters.region) {
      params.handling_area = filters.region
    }

    const res = await api.SearchComplaints(params)
    if (res.code === 2000) {
      currentList.value = res.data.data || []
      pagination.total = res.data.total || 0
      state.hasFetchedList = true
      ElMessage.success(`找到 ${pagination.total} 条相关诉求`)
    } else {
      ElMessage.error(res.msg || '搜索失败')
    }
  } catch (error: any) {
    console.error('搜索失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    loading.list = false
  }
}

// 应用筛选（查询按钮）
const applyFilters = () => {
  pagination.page = 1
  onFetchList()
}

// 重置筛选
const resetFilters = () => {
  filters.keywords = [...state.keywords]
  filters.dateRange = []
  filters.region = ''
  pagination.page = 1
}

// 分页变化
const onPageChange = (page: number) => {
  pagination.page = page
  onFetchList()
}

// 4. 智能分析
const onSmartAnalyze = async () => {
  loading.analysis = true
  try {
    const params: any = {
      title: state.topic,
      keywords: filters.keywords
    }

    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_time = filters.dateRange[0]
      params.end_time = filters.dateRange[1]
    }
    if (filters.region) {
      params.handling_area = filters.region
    }

    const res = await api.GenerateReport(params)
    if (res.code === 2000) {
      state.analysisMarkdown = res.data.content
      state.currentReportId = res.data.report_id
      ElMessage.success('分析报告生成成功')
    } else {
      ElMessage.error(res.msg || '报告生成失败')
    }
  } catch (error: any) {
    console.error('报告生成失败:', error)
    ElMessage.error('报告生成失败，请重试')
  } finally {
    loading.analysis = false
  }
}

// 5. 导出报告
const onExportReport = async () => {
  if (!state.currentReportId) {
    ElMessage.warning('请先生成分析报告')
    return
  }

  loading.exporting = true
  try {
    const res = await api.ExportReport({ report_id: state.currentReportId })
    if (res.code === 2000) {
      const blob = await api.DownloadFile(res.data.filename)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = res.data.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('报告导出成功')
    } else {
      ElMessage.error(res.msg || '导出失败')
    }
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    loading.exporting = false
  }
}

// 关键词管理
const toggleAll = () => {
  if (allSelected.value) {
    filters.keywords = []
  } else {
    filters.keywords = [...state.keywords]
  }
}

const toggleKeyword = (kw: string) => {
  const index = filters.keywords.indexOf(kw)
  if (index > -1) {
    filters.keywords.splice(index, 1)
  } else {
    filters.keywords.push(kw)
  }
}

const addKeyword = () => {
  if (keywordInput.value.trim()) {
    state.keywords.push(keywordInput.value.trim())
    keywordInput.value = ''
  }
}

const removeKeyword = (kw: string) => {
  const index = state.keywords.indexOf(kw)
  if (index > -1) {
    state.keywords.splice(index, 1)
    // 同时从筛选中移除
    const filterIndex = filters.keywords.indexOf(kw)
    if (filterIndex > -1) {
      filters.keywords.splice(filterIndex, 1)
    }
  }
}

const startEdit = (idx: number) => {
  editingIndex.value = idx
  editingValue.value = state.keywords[idx]
}

const confirmEdit = () => {
  if (editingIndex.value !== null && editingValue.value.trim()) {
    const oldValue = state.keywords[editingIndex.value]
    state.keywords[editingIndex.value] = editingValue.value.trim()

    // 更新筛选中的关键词
    const filterIndex = filters.keywords.indexOf(oldValue)
    if (filterIndex > -1) {
      filters.keywords[filterIndex] = editingValue.value.trim()
    }

    editingIndex.value = null
  }
}

// 打开工单详情
const openDetail = (row: ComplaintItem) => {
  if (complaintDetailRef.value) {
    complaintDetailRef.value.open(row.serial_number)
  }
}
</script>

<style scoped lang="scss">
.thematic-analysis-page {
  padding: 16px;

  .top-card,
  .section-card {
    margin-bottom: 16px;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .card-title {
        font-weight: 600;
        font-size: 16px;
      }
    }
  }

  .summary-content {
    line-height: 1.8;
    color: #606266;
  }

  .keyword-section {
    .keyword-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;

      .keyword-tag {
        cursor: pointer;
        user-select: none;
      }
    }

    .keyword-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .filter-form {
    margin-bottom: 16px;
  }

  .pagination-wrapper {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
  }

  // Markdown 样式
  .markdown-body {
    padding: 20px;
    background: #fff;
    border-radius: 4px;
  }
}
</style>
