/**
 * 风险标注浏览 API 接口
 * 调用 Django 后端，查询 risk_tags 表
 */
import { request } from '/@/utils/service'
import type {
  ApiResponse,
  ComplaintListResponse,
  RiskAnnotationDetail
} from './types'

/**
 * 1. 获取已标注风险的诉求列表
 * 从数据库 risk_tags 表查询 is_risk=1 的记录
 */
export function getRiskAnnotationList(params: {
  page: number
  size: number
}): Promise<ApiResponse<ComplaintListResponse>> {
  return request({
    url: 'api/risk_warning/annotation/risk/list',
    method: 'get',
    params
  })
}

/**
 * 2. 获取某个诉求的风险标注详情
 * 联表查询 complaints + risk_tags
 */
export function getRiskAnnotationDetail(
  complaintId: string
): Promise<ApiResponse<RiskAnnotationDetail>> {
  return request({
    url: `api/risk_warning/annotation/risk/detail/${complaintId}`,
    method: 'get'
  })
}
