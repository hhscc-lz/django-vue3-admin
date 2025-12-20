/**
 * 群体事件 TypeScript 类型定义
 */

/**
 * 群体事件数据接口
 */
export interface GroupEvent {
  id: number
  title: string
  trigger_complaint_id: string
  trigger_complaint_title?: string | null
  complaint_count: number
  region: string | null
  created_at: string
}

/**
 * 群体事件详情接口（包含关联工单）
 */
export interface GroupEventDetail extends GroupEvent {
  related_complaints: RelatedComplaint[]
}

/**
 * 关联工单接口
 */
export interface RelatedComplaint {
  id: string
  title: string | null
  region: string | null
  accept_time: string | null
  status: string | null
  complete_time: string | null
  category_level1: string | null
  category_level2: string | null
}

/**
 * 群体事件关联工单（带事件信息）
 */
export interface GroupEventComplaint {
  id: number
  group_event_id: number
  event_title: string
  complaint_id: string
  complaint_detail: RelatedComplaint
  created_at: string
}

/**
 * 查询参数接口
 */
export interface GroupEventQuery {
  page?: number
  limit?: number
  created_at_start?: string  // 创建时间开始
  created_at_end?: string    // 创建时间结束
  created_at_range?: string[] // 创建时间范围（前端用）
  region?: string            // 区域
  title?: string             // 标题搜索
}
