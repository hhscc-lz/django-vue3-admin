/**
 * 专题标注API接口
 */
import { request } from '/@/utils/service'
import type { ApiResponse, ComplaintListResponse, TopicAnnotationDetail } from './types'

/**
 * 获取专题标注列表
 * @param params 分页参数
 */
export function getTopicAnnotationList(params: {
  page: number
  size: number
}): Promise<ApiResponse<ComplaintListResponse>> {
  return request({
    url: 'api/topic_annotation/annotation/topic/list',
    method: 'get',
    params
  })
}

/**
 * 获取专题标注详情
 * @param complaintId 工单编号
 */
export function getTopicAnnotationDetail(
  complaintId: string
): Promise<ApiResponse<TopicAnnotationDetail>> {
  return request({
    url: `api/topic_annotation/annotation/topic/detail/${complaintId}`,
    method: 'get'
  })
}
