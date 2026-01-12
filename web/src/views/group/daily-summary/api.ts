/**
 * 群体事件每日摘要 API
 */
import { request, llmRequest } from '/@/utils/service'
import type { PageRes } from '@fast-crud/fast-crud'
import type { DailySummary, DailySummaryQuery, RegeneratedSummary } from './types'

// API 基础路径
export const apiPrefix = '/api/group_event/daily-summary'

/**
 * 获取摘要列表（分页）
 */
export function GetList(query: DailySummaryQuery): Promise<PageRes<DailySummary>> {
  return request({
    url: apiPrefix + '/list/',
    method: 'get',
    params: query
  })
}

/**
 * 获取指定日期摘要
 */
export function GetByDate(date: string): Promise<DailySummary> {
  return request({
    url: apiPrefix + `/${date}`,
    method: 'get'
  })
}

/**
 * 重新生成摘要（不入库）
 * 调用 LLM 服务生成新摘要
 */
export function Regenerate(date: string): Promise<RegeneratedSummary> {
  return llmRequest({
    url: '/daily-summary/regenerate',
    method: 'post',
    data: { date }
  })
}
