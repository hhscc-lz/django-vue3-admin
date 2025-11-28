/**
 * 风险标注浏览类型定义
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
 * 诉求列表项（已标注风险，但左侧列表不显示标注信息）
 */
export interface ComplaintItem {
  complaint_id: string      // 工单编号
  title: string             // 诉求标题
  content: string           // 诉求内容
  accept_time: string       // 受理时间
  status: string            // 工单状态
  region: string            // 所属区域
  // 左侧列表不显示风险标注信息（模拟待标注状态）
  is_risk?: boolean         // 是否风险件（可选）
  risk_category?: string    // 风险类别（可选）
  annotated_at?: string     // 标注时间（可选）
}

/**
 * 诉求列表响应
 */
export interface ComplaintListResponse {
  data: ComplaintItem[]
  total: number
  page: number
  size: number
}

/**
 * 风险标注详情
 */
export interface RiskAnnotationDetail {
  // 诉求基本信息
  complaint: {
    complaint_id: string
    title: string
    content: string
    accept_time: string
    status: string
    region: string
    complainant_name?: string
    complainant_phone?: string
    handle_department?: string
    source_channel?: string
  }
  // 风险标注信息
  risk: {
    is_risk: boolean
    risk_category: string    // 风险类别
    risk_reason: string      // 判定原因
    annotated_at: string     // 标注时间
  }
}
