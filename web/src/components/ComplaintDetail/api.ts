/**
 * 工单详情 API 接口
 */
import { request } from '/@/utils/service'
import type { ComplaintFullDetail } from './types'

// API 路径前缀
export const apiPrefix = '/api/complaint/complaints'

/**
 * 标准响应格式
 */
interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

/**
 * 获取工单完整详情
 * @param id 工单编号
 * @returns 工单完整详情数据
 */
export function GetFullDetail(id: string): Promise<ApiResponse<ComplaintFullDetail>> {
  return request({
    url: `${apiPrefix}/${id}/full-detail/`,
    method: 'get'
  })
}
