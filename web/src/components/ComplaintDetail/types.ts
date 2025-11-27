/**
 * 工单详情相关类型定义
 */

/**
 * 风险信息
 */
export interface RiskInfo {
  id: number
  is_risk: boolean
  risk_category: string | null
  risk_reason: string | null
  created_at: string | null
}

/**
 * 工单完整详情
 */
export interface ComplaintFullDetail {
  // 主键
  id: string

  // 基础信息
  complainant_name: string | null
  complainant_phone: string | null

  // 诉求内容
  title: string | null
  content: string | null

  // 分类信息
  category_level1: string | null
  category_level2: string | null
  category_level3: string | null
  category_level4: string | null
  order_type: string | null
  complaint_type: string | null
  region: string | null

  // 流程信息
  accept_time: string | null
  status: string | null
  source_channel: string | null
  complete_time: string | null
  reply_time: string | null
  reply_person: string | null
  callback_result: string | null
  handle_department: string | null

  // 统计信息
  urge_count: number | null
  supplement_count: number | null
  repeat_count: number | null

  // 关联信息
  risk_info: RiskInfo | null
}
