/**
 * 空间标注浏览 API 接口
 * 调用 Django 后端，查询 spatial_tags 表
 */
import { request } from '/@/utils/service'
import type {
  ApiResponse,
  ComplaintListResponse,
  SpatialAnnotationDetail
} from './types'

/**
 * 1. 获取已标注空间信息的诉求列表
 * 从数据库 spatial_tags 表查询记录
 */
export function getSpatialAnnotationList(params: {
  page: number
  size: number
}): Promise<ApiResponse<ComplaintListResponse>> {
  return request({
    url: 'api/spatial_annotation/annotation/spatial/list',
    method: 'get',
    params
  })
}

/**
 * 2. 获取某个诉求的空间标注详情
 * 联表查询 complaints + spatial_tags
 */
export function getSpatialAnnotationDetail(
  complaintId: string
): Promise<ApiResponse<SpatialAnnotationDetail>> {
  return request({
    url: `api/spatial_annotation/annotation/spatial/detail/${complaintId}`,
    method: 'get'
  })
}
