/**
 * 专题标注类型定义
 */

// 诉求列表项
export interface ComplaintItem {
  complaint_id: string
  title: string
  content: string
  accept_time: string
  status: string
  region: string
  // 左侧列表不显示专题标注信息（模拟待标注状态）
  topic_name?: string
  annotated_at?: string
}

// 专题标注详情
export interface TopicAnnotationDetail {
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
  topic: {
    topic_name: string
    topic_fields: Record<string, any>  // JSON对象，字段名和值都是动态的
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
