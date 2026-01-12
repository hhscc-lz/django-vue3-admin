/**
 * 群体事件每日摘要类型定义
 */

import type { PageQuery } from '@fast-crud/fast-crud'

/**
 * 每日摘要数据
 */
export interface DailySummary {
  id: number
  summary_date: string
  title: string
  content: string
  event_count: number
  event_ids: number[]
  created_at: string
}

/**
 * 摘要列表查询参数
 */
export interface DailySummaryQuery extends PageQuery {
  summary_date?: string
}

/**
 * 重新生成响应
 */
export interface RegeneratedSummary {
  summary_date: string
  title: string
  content: string
  event_count: number
  event_ids: number[]
}
