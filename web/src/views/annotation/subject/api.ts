/**
 * 主体标注API接口
 */
import { request } from '/@/utils/service'
import type { ApiResponse, ComplaintListResponse, SubjectAnnotationDetail } from './types'

/**
 * 获取主体标注列表
 * @param params 分页参数
 */
export function getSubjectAnnotationList(params: {
  page: number
  size: number
}): Promise<ApiResponse<ComplaintListResponse>> {
  return request({
    url: 'api/subject_annotation/annotation/subject/list',
    method: 'get',
    params
  })
}

/**
 * 获取主体标注详情
 * @param complaintId 工单编号
 */
export function getSubjectAnnotationDetail(
  complaintId: string
): Promise<ApiResponse<SubjectAnnotationDetail>> {
  return request({
    url: `api/subject_annotation/annotation/subject/detail/${complaintId}`,
    method: 'get'
  })
}
