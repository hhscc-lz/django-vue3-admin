/**
 * AI 专题分析类型定义
 */

/**
 * 标准 API 响应格式
 */
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
  count?: number
}

/**
 * 1. 专业问题分析
 */
export interface DescribeProblemRequest {
  title: string
}

export interface DescribeProblemResponse {
  title: string
  explanation: string
}

/**
 * 2. 关键词提取
 */
export interface ExtractKeywordsRequest {
  title: string
}

export interface ExtractKeywordsResponse {
  title: string
  keywords: string[]
}

/**
 * 3. 诉求数据搜索
 */
export interface SearchComplaintsRequest {
  keywords: string[]
  start_time?: string
  end_time?: string
  handling_area?: string
  page?: number
  size?: number
}

export interface ComplaintItem {
  serial_number: string
  title: string
  content: string
  time: string
  handling_area: string
  status: string
  source: string
}

export interface SearchComplaintsResponse {
  data: ComplaintItem[]
  total: number
  page: number
  size: number
}

/**
 * 4. 生成分析报告
 */
export interface GenerateReportRequest {
  title: string
  keywords: string[]
  start_time?: string
  end_time?: string
  handling_area?: string
}

export interface GenerateReportResponse {
  report_id: string
  title: string
  status: string
  content: string  // Markdown 格式
  data_count: number
  generated_at: string
}

/**
 * 5. 导出分析报告
 */
export interface ExportReportRequest {
  report_id: string
}

export interface ExportReportResponse {
  filename: string
  download_url: string
}
