/**
 * 群体事件 API
 */
import { request } from '/@/utils/service'
import type { PageQuery, PageRes, InfoReq } from '@fast-crud/fast-crud'
import type {
  GroupEvent,
  GroupEventDetail,
  GroupEventComplaint,
  GroupEventQuery
} from './types'

// API 基础路径
export const apiPrefix = '/api/group_event/group-events'

/**
 * 获取群体事件列表
 */
export function GetList(query: GroupEventQuery): Promise<PageRes<GroupEvent>> {
  return request({
    url: apiPrefix + '/',
    method: 'get',
    params: query
  })
}

/**
 * 获取群体事件详情
 */
export function GetDetail(id: InfoReq): Promise<GroupEventDetail> {
  return request({
    url: apiPrefix + `/${id}/`,
    method: 'get'
  })
}

/**
 * 获取某事件的关联工单列表（分页）
 */
export function GetRelatedComplaints(
  eventId: number,
  query: PageQuery
): Promise<PageRes<GroupEventComplaint>> {
  return request({
    url: apiPrefix + `/${eventId}/related-complaints/`,
    method: 'get',
    params: query
  })
}
