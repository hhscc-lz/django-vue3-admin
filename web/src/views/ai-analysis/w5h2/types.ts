/**
 * 5W2H 分析类型定义
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
 * 查询请求
 */
export interface SearchRequest {
  start_time?: string     // 开始时间
  end_time?: string       // 结束时间
  region?: string         // 地区
  keywords?: string       // 关键词
  serial_number?: string  // 工单编号
  type?: string           // 诉求类型
  page: number
  size: number
}

/**
 * 诉求列表项
 */
export interface ComplaintItem {
  serial_number: string
  title: string
  content: string
  time: string
  region: string
  status: string
  type: string
}

/**
 * 查询响应
 */
export interface SearchResponse {
  data: ComplaintItem[]
  total: number
  page: number
  size: number
}

/**
 * 诉求详情（简化的5W2H结构，不分模块）
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
 * 大模型分析请求
 */
export interface AnalyzeRequest {
  start_time?: string
  end_time?: string
  region?: string
  keywords?: string
  serial_number?: string
  type?: string
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
