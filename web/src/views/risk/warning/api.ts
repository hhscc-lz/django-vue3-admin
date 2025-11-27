/**
 * 风险预警 API
 */
import { request } from '/@/utils/service'
import type { PageQuery, PageRes, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud'

// API 基础路径
export const apiPrefix = '/api/risk_warning/risk-tags'

/**
 * 风险标注数据接口
 */
export interface RiskTag {
  id: number
  complaint_id: string
  is_risk: boolean
  risk_category: string | null
  risk_reason: string | null
  created_at: string
  // 关联的工单字段
  complaint_title: string | null
  complaint_region: string | null
  complaint_accept_time: string | null
  complaint_status: string | null
  complaint_complete_time: string | null
  complaint_category_level1: string | null
  complaint_category_level2: string | null
}

/**
 * 查询参数接口
 */
export interface RiskTagQuery extends PageQuery {
  accept_time_start?: string  // 受理时间开始
  accept_time_end?: string    // 受理时间结束
  accept_time_range?: string[] // 受理时间范围（前端用）
  risk_category?: string      // 风险类别
  is_risk?: boolean           // 是否风险
  complaint_id?: string       // 工单编号
  region?: string             // 所属区域
}

/**
 * 获取列表
 */
export function GetList(query: RiskTagQuery): Promise<PageRes<RiskTag>> {
  return request({
    url: apiPrefix + '/',
    method: 'get',
    params: query
  })
}

/**
 * 获取详情
 */
export function GetObj(id: InfoReq): Promise<RiskTag> {
  return request({
    url: apiPrefix + `/${id}/`,
    method: 'get'
  })
}

/**
 * 导出数据
 */
export async function Export(query: RiskTagQuery): Promise<Blob> {
  const response: any = await request({
    url: apiPrefix + '/export/',
    method: 'get',
    params: query,
    responseType: 'blob'
  })
  // 当 responseType 为 blob 时，响应拦截器返回完整的 response 对象
  // 需要从 response.data 中提取 Blob
  return response.data || response
}

/**
 * 导出文件下载助手
 */
export function downloadExportFile(blob: Blob, filename?: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename || `风险预警数据_${new Date().getTime()}.xlsx`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
