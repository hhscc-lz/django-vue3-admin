/**
 * 综合查询类型定义
 */

/**
 * 标准 API 响应格式
 */
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

/**
 * 诉求详情
 */
export interface ComplaintDetail {
  // What - 诉求概况
  serial_number: string
  title: string
  content: string
  type: string
  source: string

  // Who - 诉求人/责任主体
  phone?: string
  contact?: string
  department?: string

  // When - 时间线
  request_time: string
  register_time?: string
  finish_time?: string
  answer_time?: string

  // Where - 地址
  region: string
  address?: string

  // Why - 问题成因
  category?: string
  risk_level?: string

  // How - 处理流程
  status: string
  handle_type?: string
  answer_content?: string

  // How much - 评价
  satisfaction?: string
  rating?: string
}

/**
 * 分析摘要
 */
export interface AnalysisSummary {
  total: number
  time_range?: {
    start: string
    end: string
  }
  top_categories?: Array<{
    label: string
    count: number
  }>
  top_regions?: Array<{
    label: string
    count: number
  }>
}

/**
 * 大模型分析响应
 */
export interface AnalyzeResponse {
  analysis: string      // Markdown 格式的分析内容
  summary: AnalysisSummary
}

/**
 * 导出报告请求
 */
export interface ExportReportRequest {
  analysis: string
  summary: AnalysisSummary
}

// ==================== 综合查询相关类型 ====================

/**
 * 查询条件
 */
export interface FilterCondition {
  field: string
  operator: string
  value: any
}

/**
 * 综合查询请求
 */
export interface ComprehensiveSearchRequest {
  filters: FilterCondition[]
  logic: 'AND' | 'OR'
  page: number
  size: number
  sort_field?: string
  sort_order?: 'asc' | 'desc'
}

/**
 * 综合查询分析请求
 */
export interface ComprehensiveAnalyzeRequest {
  filters: FilterCondition[]
  logic: 'AND' | 'OR'
}

/**
 * 综合查询响应
 */
export interface ComprehensiveSearchResponse {
  data: Array<Record<string, any>>
  total: number
  page: number
  size: number
}

/**
 * 字段配置项
 */
export interface FieldConfigItem {
  field: string
  label: string
  es_type: string
  control: string
  operators: string[]
  options?: Array<{ value: string; label: string }>
  nested_path?: string
  dynamic_options?: boolean
}

/**
 * 字段配置响应
 */
export interface FieldConfigResponse {
  fields: FieldConfigItem[]
}

/**
 * 字段可选值请求
 */
export interface FieldOptionRequest {
  field: string
  size?: number
  parent_filters?: FilterCondition[]  // 父级字段过滤条件（用于级联）
}

/**
 * 字段可选值项
 */
export interface FieldOption {
  value: string
  label: string
  count?: number
}

/**
 * 字段可选值响应
 */
export interface FieldOptionResponse {
  field: string
  options: FieldOption[]
}
