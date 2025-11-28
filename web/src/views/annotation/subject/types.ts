/**
 * 主体标注类型定义
 */

// 诉求列表项
export interface ComplaintItem {
  complaint_id: string
  title: string
  content: string
  accept_time: string
  status: string
  region: string
  // 左侧列表不显示主体标注信息（模拟待标注状态）
  subject_name?: string
  subject_type?: string
  annotated_at?: string
}

// 主体标注详情
export interface SubjectAnnotationDetail {
  complaint: {
    complaint_id: string
    title: string
    content: string
    accept_time: string
    status: string
    region: string
    complainant_name: string
    complainant_phone: string
    handle_department: string
    source_channel: string
  }
  subject: {
    subject_name: string
    subject_type: string
    industry: string
    scale: string
    complaint_nature: string
    model: string
    annotated_at: string
  }
}

// 诉求列表响应
export interface ComplaintListResponse {
  data: ComplaintItem[]
  total: number
  page: number
  size: number
}

// API响应
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}
