/**
 * 空间标注浏览类型定义
 */

/**
 * 标准 API 响应格式
 */
export interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

/**
 * 诉求列表项（已标注空间信息，但左侧列表不显示标注信息）
 */
export interface ComplaintItem {
  complaint_id: string      // 工单编号
  title: string             // 诉求标题
  content: string           // 诉求内容
  accept_time: string       // 受理时间
  status: string            // 工单状态
  region: string            // 所属区域
  // 左侧列表不显示空间标注信息（模拟待标注状态）
  address?: string          // 提取的诉求地址（可选）
  address_type?: string     // 地址类型（可选）
  annotated_at?: string     // 标注时间（可选）
}

/**
 * 诉求列表响应
 */
export interface ComplaintListResponse {
  data: ComplaintItem[]
  total: number
  page: number
  size: number
}

/**
 * 空间标注详情
 */
export interface SpatialAnnotationDetail {
  // 诉求基本信息
  complaint: {
    complaint_id: string
    title: string
    content: string
    accept_time: string
    status: string
    region: string
    complainant_name?: string
    complainant_phone?: string
    handle_department?: string
    source_channel?: string
  }
  // 空间标注信息
  spatial: {
    address: string           // 提取的诉求地址
    address_type: string      // 地址类型
    longitude: number | null  // 经度
    latitude: number | null   // 纬度
    district: string          // 区县
    street: string            // 街道
    community: string         // 小区
    annotated_at: string      // 标注时间
  }
}
