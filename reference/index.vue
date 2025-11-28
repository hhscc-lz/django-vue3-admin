<template>
  <div class="ai-topic-page">
      <!-- 顶部：专题输入 + 操作按钮 -->
      <el-card class="top-card" shadow="never">
        <template #header>
          <div class="top-card__header">
            <div class="title">
              <el-icon><CollectionTag /></el-icon>
              <span>专题分析</span>
            </div>
          </div>
        </template>
        <el-row :gutter="12" class="top-action-row">
          <el-col :span="24" :xs="24">
            <el-input
              v-model="state.topic"
              placeholder="请输入专题问题，例如：道路积水"
              clearable
              size="large"
              @keyup.enter="onSummarize"
            >
              <template #prefix>
                <el-icon><EditPen /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="24" :xs="24">
            <div class="btn-group below-input">
              <el-button size="default" type="primary" :loading="loading.summarize" @click="onSummarize">
                <el-icon><Document /></el-icon>
                概要描述
              </el-button>
              <el-button size="default" :loading="loading.features" @click="onExtractFeatures">
                <el-icon><Cpu /></el-icon>
                特征提取
              </el-button>
              <el-button size="default" :loading="loading.list" :disabled="!canFetchList" @click="onFetchList">
                <el-icon><List /></el-icon>
                获取问题清单
              </el-button>
              <el-button size="default" :loading="loading.analysis" :disabled="!canAnalyze" @click="onSmartAnalyze">
                <el-icon><MagicStick /></el-icon>
                智能分析
              </el-button>
              <el-button size="default" type="success" :loading="loading.exporting" @click="onExportReport">
                <el-icon><Download /></el-icon>
                导出报告
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 概要描述 -->
      <el-card class="section-card" shadow="never" v-loading="loading.summarize">
        <template #header>
          <div class="section-header">
            <div class="title">
              <el-icon><Document /></el-icon>
              <span>概要描述</span>
            </div>
          </div>
        </template>
        <div class="summary-text" v-if="state.summary" v-html="formatTextWithBreaks(state.summary)">
        </div>
        <el-empty v-else description="点击上方“概要描述”以生成内容" />
      </el-card>

      <!-- 特征提取（关键词，可编辑/新增/删除） -->
      <el-card class="section-card" shadow="never" v-loading="loading.features">
        <template #header>
          <div class="section-header">
            <div class="title">
              <el-icon><Cpu /></el-icon>
              <span>特征关键词</span>
            </div>
          </div>
        </template>
        <div class="kw-row">
          <div class="keyword-wrap">
            <el-tag class="kw-tag kw-all" size="large" :class="{ 'is-active': allSelected }" @click="toggleAll">全部</el-tag>
            <div v-for="(kw, idx) in state.keywords" :key="idx" class="kw-item">
              <template v-if="editingIndex !== idx">
                <el-tag
                  size="large"
                  class="kw-tag"
                  effect="light"
                  :class="{ 'is-active': filters.keywords.includes(kw) }"
                  closable
                  @click="toggleKeyword(kw)"
                  @dblclick.stop="startEdit(idx)"
                  @close="removeKeyword(kw)"
                >
                  {{ kw }}
                </el-tag>
              </template>
              <template v-else>
                <el-input
                  v-model="editingValue"
                  size="small"
                  class="kw-edit-input"
                  maxlength="16"
                  show-word-limit
                  @keyup.enter="confirmEdit"
                  @blur="confirmEdit"
                />
              </template>
            </div>
          </div>
          <div class="kw-add">
            <el-input
              v-model="keywordInput"
              placeholder="输入关键词后回车或点击添加"
              clearable
              size="small"
              @keyup.enter="addKeyword"
              :maxlength="16"
              show-word-limit
              style="max-width: 280px"
            />
            <el-button size="small" class="btn-soft" @click="addKeyword">添加</el-button>
            <el-button size="small" class="chip-save" @click="saveKeywords">保存</el-button>
          </div>
        </div>
      </el-card>

      <!-- 问题清单（检索条件 + 列表） -->
      <el-card class="section-card" shadow="never" v-loading="loading.list" v-if="state.hasFetchedList">
        <template #header>
          <div class="section-header">
            <div class="title">
              <el-icon><List /></el-icon>
              <span>问题清单</span>
            </div>
          </div>
        </template>
        <el-form :model="filters" label-width="90px" class="filter-form">
          <el-row :gutter="12">
            <el-col :span="24" :xs="24">
              <el-form-item label="关键词">
                <el-select v-model="filters.keywords" multiple filterable clearable placeholder="选择或输入关键词">
                  <el-option v-for="kw in state.keywords" :key="kw" :label="kw" :value="kw" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="12">
            <el-col :span="12" :xs="24">
              <el-form-item label="地区">
                <el-cascader
                  v-model="filters.region"
                  :options="mockRegions"
                  clearable
                  :props="{ emitPath: false }"
                  placeholder="请选择市/区"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12" :xs="24">
              <el-form-item label="时间范围">
                <el-date-picker
                  v-model="filters.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <div class="filter-btns-center">
            <el-button type="primary" @click="applyFilters"><el-icon><Search /></el-icon>查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </div>
        </el-form>

        <template v-if="currentList.length > 0">
          <el-table :data="pagedList" border stripe style="width: 100%">
            <el-table-column prop="serial_number" label="诉求编号" width="160" />
            <el-table-column prop="title" label="标题" min-width="220" />
            <el-table-column label="内容摘要" min-width="320">
              <template #default="{ row }">
                <span class="text-ellipsis">{{ row.content }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" width="160" />
            <el-table-column prop="handling_area" label="处理地区" width="140" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="source" label="来源" width="120" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" class="btn-soft" @click="openDetail(row)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <template v-else>
          <el-empty description="请设置筛选条件并点击查询按钮获取数据" />
        </template>

        <div class="table-footer" v-if="currentList.length > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            layout="total, prev, pager, next, jumper"
            @current-change="onPageChange"
          />
        </div>
      </el-card>

      <!-- 智能分析（Markdown 预览占位） -->
      <el-card class="section-card" shadow="never" v-loading="loading.analysis" v-if="state.hasFetchedList">
        <template #header>
          <div class="section-header">
            <div class="title">
              <el-icon><MagicStick /></el-icon>
              <span>智能分析</span>
            </div>
          </div>
        </template>
        <template v-if="state.analysisMarkdown">
          <el-scrollbar height="360px">
            <div class="md-preview" v-html="md.render(state.analysisMarkdown)"></div>
          </el-scrollbar>
        </template>
        <el-empty v-else description="点击上方“智能分析”以生成内容" />
      </el-card>


      <!-- 使用公共详情组件 -->
      <ComplaintDetail
        v-model:visible="detailVisible"
        :complaint-id="selectedComplaintId"
      />
  </div>
  
</template>

<script setup lang="ts" name="topicAnalysis">
import { reactive, computed, ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { Local } from '/@/utils/storage'
import { CollectionTag, EditPen, Document, Cpu, List, MagicStick, Download, Search } from '@element-plus/icons-vue'
import { useThematicAnalysisApi } from '/@/api/ai-analysis/thematic'
import type { ComplaintItem, SearchComplaintsRequest } from '/@/api/ai-analysis/thematic-types'
import ComplaintDetail from '/@/components/ComplaintDetail/index.vue'
import MarkdownIt from 'markdown-it'
import { Document as DocxDocument, Packer, Paragraph, TextRun, HeadingLevel } from 'docx'

// 页面状态
const state = reactive({
  topic: '',
  summary: '',
  keywords: [] as string[],
  analysisMarkdown: '',
  // 流程控制
  hasExtractedFeatures: false,
  hasFetchedList: false,
  // API相关状态
  currentReportId: '', // 当前生成的报告ID
  searchParams: {} as SearchComplaintsRequest, // 当前搜索参数
})

// 加载状态
const loading = reactive({
  summarize: false,
  features: false,
  list: false,
  analysis: false,
  exporting: false,
})

// 详情对话框
const detailVisible = ref(false)
const selectedComplaintId = ref<string>('')
// 关键词编辑/新增
const keywordInput = ref('')
const editingIndex = ref<number | null>(null)
const editingValue = ref('')

// 检索条件
const filters = reactive({
  keywords: [] as string[],
  dateRange: [] as string[],
  region: '',
  request_type: '',
  status: '',
  source: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 流程控制：按钮可用状态
const canFetchList = computed(() => state.hasExtractedFeatures)
const canAnalyze = computed(() => state.hasFetchedList)

// Mock: 行政区（简单两级）
const mockRegions = [
  {
    value: '海口市', label: '海口市', children: [
      { value: '龙华区', label: '龙华区' },
      { value: '美兰区', label: '美兰区' },
      { value: '琼山区', label: '琼山区' },
      { value: '秀英区', label: '秀英区' },
    ]
  },
  {
    value: '三亚市', label: '三亚市', children: [
      { value: '吉阳区', label: '吉阳区' },
      { value: '天涯区', label: '天涯区' },
    ]
  }
]


// 当前显示的数据列表（通过查询按钮获取）
const currentList = ref<ComplaintItem[]>([])

// 初始化API实例
const thematicApi = useThematicAnalysisApi()

// 初始化Markdown渲染器
const md = new MarkdownIt({
  html: true,        // 启用HTML标签
  linkify: true,     // 自动转换URL为链接
  typographer: true, // 启用排版特性
  breaks: true       // 转换换行符为<br>
})

const pagedList = computed(() => {
  // 由于API已支持分页，直接返回当前列表
  return currentList.value
})

// 分页变化处理
async function onPageChange(page: number) {
  pagination.page = page

  // 如果有搜索参数，重新调用API获取对应页面的数据
  if (state.searchParams.keywords && state.searchParams.keywords.length > 0) {
    loading.list = true
    try {
      const searchParams = {
        ...state.searchParams,
        page: pagination.page,
        size: pagination.pageSize
      }

      const response = await thematicApi.searchComplaints(searchParams)

      if (response.code === 2000) {
        currentList.value = response.data.data || []
        pagination.total = response.data.total || 0
      } else {
        ElMessage.error(response.msg || '获取数据失败')
      }
    } catch (error: any) {
      console.error('分页API调用失败:', error)
      ElMessage.error('获取数据失败，请重试')
    } finally {
      loading.list = false
    }
  }
}


// 交互：概要描述（调用真实API）
async function onSummarize() {
  if (!state.topic.trim()) {
    ElMessage.warning('请先输入专题问题')
    return
  }

  loading.summarize = true
  try {
    const response = await thematicApi.describeProblem({
      title: state.topic.trim()
    })

    if (response.code === 2000) {
      state.summary = response.data.explanation
      ElMessage.success('概要描述生成成功')
    } else {
      ElMessage.error(response.msg || '概要描述生成失败')
    }
  } catch (error: any) {
    console.error('概要描述API调用失败:', error)
    ElMessage.error('概要描述生成失败，请重试')
  } finally {
    loading.summarize = false
  }
}

// 重置流程状态
function resetWorkflow() {
  state.hasExtractedFeatures = false
  state.hasFetchedList = false
  state.analysisMarkdown = ''
}

// 交互：特征提取（调用真实API）
async function onExtractFeatures() {
  if (!state.topic.trim()) {
    ElMessage.warning('请先输入专题问题')
    return
  }

  // 重置后续流程
  resetWorkflow()

  loading.features = true
  try {
    const response = await thematicApi.extractKeywords({
      title: state.topic.trim()
    })

    if (response.code === 2000) {
      state.keywords = response.data.keywords || []
      filters.keywords = [...state.keywords]
      state.hasExtractedFeatures = true
      ElMessage.success(`成功提取 ${state.keywords.length} 个关键词`)
    } else {
      ElMessage.error(response.msg || '关键词提取失败')
    }
  } catch (error: any) {
    console.error('关键词提取API调用失败:', error)
    ElMessage.error('关键词提取失败，请重试')
  } finally {
    loading.features = false
  }
}

// 查看详情
function openDetail(row: ComplaintItem) {
  if (!row.serial_number) {
    ElMessage.warning('无法获取详情：缺少诉求编号')
    return
  }

  // 直接设置诉求ID并显示弹窗，组件会自动加载数据
  selectedComplaintId.value = row.serial_number
  detailVisible.value = true
}

// 关键词：新增/删除/编辑
function addKeyword() {
  const v = (keywordInput.value || '').trim()
  if (!v) return
  if (!state.keywords.includes(v)) {
    state.keywords.push(v)
    filters.keywords.push(v)
  }
  keywordInput.value = ''
}
function removeKeyword(kw: string) {
  state.keywords = state.keywords.filter(k => k !== kw)
  // 同步过滤条件
  filters.keywords = filters.keywords.filter(k => k !== kw)
}
function startEdit(idx: number) {
  editingIndex.value = idx
  editingValue.value = state.keywords[idx]
}
function confirmEdit() {
  if (editingIndex.value === null) return
  const v = (editingValue.value || '').trim()
  const old = state.keywords[editingIndex.value]
  if (v && !state.keywords.includes(v)) {
    state.keywords[editingIndex.value] = v
    // 更新过滤条件中对应值
    filters.keywords = filters.keywords.map(k => (k === old ? v : k))
  }
  editingIndex.value = null
  editingValue.value = ''
}


// 关键词选择与全选
const allSelected = computed(() => state.keywords.length > 0 && filters.keywords.length === state.keywords.length)
function toggleKeyword(kw: string) {
  const i = filters.keywords.indexOf(kw)
  if (i > -1) filters.keywords.splice(i, 1)
  else filters.keywords.push(kw)
}
function toggleAll() {
  if (allSelected.value) filters.keywords = []
  else filters.keywords = [...state.keywords]
}
// 持久化
function saveKeywords() {
  Local.set('topic_keywords', state.keywords)
  Local.set('topic_keywords_selected', filters.keywords)
  ElMessage.success('已保存关键词')
}
onMounted(() => {
  const saved = Local.get('topic_keywords')
  const selected = Local.get('topic_keywords_selected')
  if (Array.isArray(saved)) state.keywords = saved
  if (Array.isArray(selected)) filters.keywords = selected
})

// 交互：获取问题清单（显示筛选和查询区域）
async function onFetchList() {
  // 重置智能分析状态
  state.analysisMarkdown = ''

  // 清空当前显示的数据
  currentList.value = []
  pagination.page = 1

  // 显示问题清单区域
  state.hasFetchedList = true

  // 立即发起首轮查询（确保区域渲染后再查询，便于展示加载状态）
  await nextTick()
  await applyFilters()
}

// 查询数据（调用真实API）
async function applyFilters() {
  if (!filters.keywords || filters.keywords.length === 0) {
    ElMessage.warning('请至少选择一个关键词进行搜索')
    return
  }

  loading.list = true
  pagination.page = 1

  try {
    // 构建搜索参数
    const searchParams: SearchComplaintsRequest = {
      keywords: filters.keywords,
      page: pagination.page,
      size: pagination.pageSize,
    }

    // 添加可选的筛选条件
    if (filters.dateRange && filters.dateRange.length === 2) {
      searchParams.start_time = filters.dateRange[0]
      searchParams.end_time = filters.dateRange[1]
    }

    if (filters.region) {
      searchParams.handling_area = filters.region
    }

    if (filters.request_type) {
      searchParams.request_type = filters.request_type
    }

    if (filters.status) {
      searchParams.status = filters.status
    }

    if (filters.source) {
      searchParams.source = filters.source
    }

    // 保存搜索参数供后续使用
    state.searchParams = { ...searchParams }

    const response = await thematicApi.searchComplaints(searchParams)

    if (response.code === 2000) {
      currentList.value = response.data.data || []
      pagination.total = response.data.total || 0
      pagination.page = response.data.page || 1
      ElMessage.success(`查询完成，共找到 ${pagination.total} 条数据`)
    } else {
      ElMessage.error(response.msg || '查询失败')
      currentList.value = []
      pagination.total = 0
    }

  } catch (error: any) {
    console.error('搜索API调用失败:', error)
    ElMessage.error('查询失败，请重试')
    currentList.value = []
    pagination.total = 0
  } finally {
    loading.list = false
  }
}

// 重置筛选条件（不影响当前显示的数据）
function resetFilters() {
  filters.keywords = []
  filters.dateRange = []
  filters.region = ''
  ElMessage.info('筛选条件已重置')
}

// 交互：智能分析（调用真实API）
async function onSmartAnalyze() {
  if (!state.topic.trim()) {
    ElMessage.warning('请先输入专题问题')
    return
  }

  if (!state.searchParams.keywords || state.searchParams.keywords.length === 0) {
    ElMessage.warning('请先完成问题清单查询后再进行智能分析')
    return
  }

  loading.analysis = true
  try {
    // 构建报告生成参数，基于当前的搜索条件
    const reportParams = {
      keywords: state.searchParams.keywords,
      title: state.topic.trim(),
      start_time: state.searchParams.start_time,
      end_time: state.searchParams.end_time,
      handling_area: state.searchParams.handling_area,
      request_type: state.searchParams.request_type,
      status: state.searchParams.status,
      source: state.searchParams.source
    }

    const response = await thematicApi.generateReport(reportParams)

    if (response.code === 2000) {
      state.analysisMarkdown = response.data.content
      state.currentReportId = response.data.report_id
      ElMessage.success(`智能分析报告生成成功，共分析 ${response.data.data_count} 条数据`)
    } else {
      ElMessage.error(response.msg || '智能分析生成失败')
    }
  } catch (error: any) {
    console.error('智能分析API调用失败:', error)
    ElMessage.error('智能分析生成失败，请重试')
  } finally {
    loading.analysis = false
  }
}

// 交互：导出报告（导出Word格式的智能分析报告）
async function onExportReport() {
  if (!state.analysisMarkdown) {
    ElMessage.warning('请先生成智能分析报告后再导出')
    return
  }

  loading.exporting = true

  try {
    // 生成Word文档
    const doc = await generateWordDocument()

    // 生成文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, '-')
    const filename = `智能分析报告_${state.topic || '未命名'}_${timestamp}.docx`

    // 导出文档
    const blob = await Packer.toBlob(doc)

    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'

    // 执行下载
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

// 生成Word文档
async function generateWordDocument(): Promise<DocxDocument> {
  const now = new Date().toLocaleString('zh-CN')

  // 解析Markdown内容为段落
  const paragraphs = parseMarkdownToParagraphs(state.analysisMarkdown)

  // 创建Word文档
  const doc = new DocxDocument({
    sections: [{
      properties: {},
      children: [
        // 标题
        new Paragraph({
          children: [
            new TextRun({
              text: "智能分析报告",
              bold: true,
              size: 32,
            }),
          ],
          heading: HeadingLevel.TITLE,
          spacing: {
            after: 400,
          },
        }),

        // 基本信息
        new Paragraph({
          children: [
            new TextRun({
              text: `专题：${state.topic}`,
              size: 24,
            }),
          ],
          spacing: {
            after: 200,
          },
        }),

        new Paragraph({
          children: [
            new TextRun({
              text: `生成时间：${now}`,
              size: 24,
            }),
          ],
          spacing: {
            after: 400,
          },
        }),

        // 智能分析内容
        ...paragraphs,
      ],
    }],
  })

  return doc
}

// 解析Markdown为Word段落
function parseMarkdownToParagraphs(markdown: string): Paragraph[] {
  if (!markdown) return []

  const paragraphs: Paragraph[] = []
  const lines = markdown.split('\n')

  for (const line of lines) {
    const trimmedLine = line.trim()

    if (!trimmedLine) {
      // 空行，添加间距
      paragraphs.push(new Paragraph({
        children: [new TextRun({ text: "" })],
        spacing: { after: 200 },
      }))
      continue
    }

    if (trimmedLine.startsWith('# ')) {
      // 一级标题
      paragraphs.push(new Paragraph({
        children: [
          new TextRun({
            text: trimmedLine.substring(2),
            bold: true,
            size: 28,
          }),
        ],
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 400, after: 200 },
      }))
    } else if (trimmedLine.startsWith('## ')) {
      // 二级标题
      paragraphs.push(new Paragraph({
        children: [
          new TextRun({
            text: trimmedLine.substring(3),
            bold: true,
            size: 26,
          }),
        ],
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 300, after: 200 },
      }))
    } else if (trimmedLine.startsWith('### ')) {
      // 三级标题
      paragraphs.push(new Paragraph({
        children: [
          new TextRun({
            text: trimmedLine.substring(4),
            bold: true,
            size: 24,
          }),
        ],
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 150 },
      }))
    } else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
      // 列表项
      paragraphs.push(new Paragraph({
        children: [
          new TextRun({
            text: `• ${trimmedLine.substring(2)}`,
            size: 22,
          }),
        ],
        spacing: { after: 100 },
        indent: { left: 400 },
      }))
    } else if (trimmedLine.match(/^\d+\. /)) {
      // 数字列表
      const match = trimmedLine.match(/^(\d+)\. (.*)/)
      if (match) {
        paragraphs.push(new Paragraph({
          children: [
            new TextRun({
              text: `${match[1]}. ${match[2]}`,
              size: 22,
            }),
          ],
          spacing: { after: 100 },
          indent: { left: 400 },
        }))
      }
    } else {
      // 普通段落
      const runs: TextRun[] = []
      const text = processInlineFormatting(trimmedLine)
      runs.push(new TextRun({
        text: text,
        size: 22,
      }))

      paragraphs.push(new Paragraph({
        children: runs,
        spacing: { after: 200 },
      }))
    }
  }

  return paragraphs
}

// 处理行内格式化（简化版）
function processInlineFormatting(text: string): string {
  // 移除Markdown格式标记，保留纯文本
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1')  // 移除粗体标记
    .replace(/\*(.*?)\*/g, '$1')      // 移除斜体标记
    .replace(/`([^`]+)`/g, '$1')      // 移除代码标记
}

// 格式化文本，处理换行符
function formatTextWithBreaks(text: string): string {
  if (!text) return ''

  // 将 \n\n 替换为段落分隔，\n 替换为换行
  return text
    .replace(/\n\n/g, '</p><p>')  // 双换行符作为段落分隔
    .replace(/\n/g, '<br>')       // 单换行符作为换行
    .replace(/^/, '<p>')          // 开头添加段落标签
    .replace(/$/, '</p>')         // 结尾添加段落标签
}


// 使用 markdown-it 渲染Markdown内容
</script>

<style scoped lang="scss">
.ai-topic-page {
  .top-card { margin-bottom: 16px; }
  .top-card__header { display: flex; align-items: center; justify-content: space-between; }
  .top-action-row { align-items: center; }
  .title { display: flex; align-items: center; gap: 8px; font-weight: 600; }
  .btn-group { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 6px; }
  .btn-group.below-input { justify-content: center; margin-top: 12px; }

  .section-card { margin-top: 16px; }
  .section-header { display: flex; align-items: center; justify-content: space-between; }

.kw-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.kw-add { display: flex; align-items: center; gap: 8px; margin-bottom: 0; margin-left: auto; }
.keyword-wrap { display: flex; flex-wrap: wrap; gap: 12px 16px; flex: 1 1 auto; min-height: 32px; }
.kw-item { display: inline-flex; align-items: center; gap: 6px; }
.kw-tag { margin: 4px 0; cursor: pointer; font-size: 14px; font-weight: 600; padding: 6px 14px; border-radius: 999px; user-select: none; }
.kw-tag {
  background: #fff;
  color: var(--el-text-color-regular);
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.kw-tag:hover {
  background: var(--el-fill-color-light);
  border-color: var(--el-border-color);
}
.kw-tag :deep(.el-tag__close) {
  color: var(--el-text-color-secondary);
}
  .kw-tag.is-active {
    background: var(--el-fill-color-light);
    border-color: var(--el-border-color);
    color: var(--el-text-color-primary);
  }
  .kw-tag.kw-all { font-weight: 700; }
  .kw-edit-input { width: 160px; }
  .summary-text {
    color: var(--el-text-color-regular);
    line-height: 1.8;
    max-height: 200px;
    overflow-y: auto;
    padding: 8px 12px;
    background: var(--el-fill-color-lighter);
    border-radius: 6px;
    border: 1px solid var(--el-border-color-light);
  }

  .summary-text :deep(p) {
    margin: 0 0 12px 0;
    line-height: 1.8;
  }

  .summary-text :deep(p:last-child) {
    margin-bottom: 0;
  }

  .filter-form { margin-bottom: 10px; }
  .filter-actions { display: none; }
  .filter-btns-center { display: flex; justify-content: center; gap: 12px; margin-top: 6px; }

  .text-ellipsis {
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }
  .table-footer { margin-top: 12px; display: flex; justify-content: flex-end; }

  .md-preview {
    padding: 16px 20px;
    line-height: 1.6;
    color: var(--el-text-color-regular);
    font-size: 14px;

    :deep(h1) {
      font-size: 24px;
      font-weight: 600;
      margin: 20px 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--el-border-color-light);
      color: var(--el-text-color-primary);
    }

    :deep(h2) {
      font-size: 20px;
      font-weight: 600;
      margin: 18px 0 14px 0;
      color: var(--el-text-color-primary);
    }

    :deep(h3) {
      font-size: 16px;
      font-weight: 600;
      margin: 16px 0 12px 0;
      color: var(--el-text-color-primary);
    }

    :deep(p) {
      margin: 0 0 12px 0;
      line-height: 1.8;
    }

    :deep(ul, ol) {
      margin: 12px 0;
      padding-left: 24px;
    }

    :deep(li) {
      margin: 6px 0;
      line-height: 1.6;
    }

    :deep(strong) {
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    :deep(em) {
      font-style: italic;
    }

    :deep(code) {
      background: var(--el-fill-color-light);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      font-size: 13px;
      color: var(--el-color-danger);
    }

    :deep(blockquote) {
      border-left: 4px solid var(--el-color-primary);
      padding-left: 16px;
      margin: 16px 0;
      color: var(--el-text-color-secondary);
      background: var(--el-fill-color-lighter);
      padding: 12px 16px;
      border-radius: 4px;
    }
  }

  /* 轻量按钮（浅色） */
  :deep(.el-button.btn-soft) {
    background: rgba(13, 109, 220, 0.08);
    color: var(--el-color-primary);
    border: 1px solid var(--gov-border-soft);
  }
  :deep(.el-button.btn-soft:hover) {
    background: rgba(13, 109, 220, 0.12);
    color: var(--el-color-primary);
    border-color: rgba(13, 109, 220, 0.2);
  }
    .chip-save {
    background: var(--el-color-warning);
    color: #fff;
    border: none;
    border-radius: 999px;
    padding: 6px 14px;
  }
  .chip-save:hover { filter: brightness(1.05); }
}
</style>
