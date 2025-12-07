/**
 * 综合查询 API 接口
 */
import { llmRequest } from '/@/utils/service'
import type {
  ApiResponse,
  ComplaintDetail,
  FieldConfigResponse,
  FieldOptionRequest,
  FieldOptionResponse,
  ComprehensiveSearchRequest,
  ComprehensiveSearchResponse,
  ComprehensiveAnalyzeRequest,
  AnalyzeResponse
} from './types'

// ==================== 综合查询API ====================

/**
 * 1. 获取所有字段配置
 */
export function getFieldConfigs(): Promise<ApiResponse<FieldConfigResponse>> {
  return llmRequest({
    url: '/llm/comprehensive/fields',
    method: 'get'
  })
}

/**
 * 2. 获取字段可选值
 */
export function getFieldOptions(
  params: FieldOptionRequest
): Promise<ApiResponse<FieldOptionResponse>> {
  return llmRequest({
    url: '/llm/comprehensive/field-options',
    method: 'post',
    data: params
  })
}

/**
 * 3. 综合查询
 */
export function comprehensiveSearch(
  params: ComprehensiveSearchRequest
): Promise<ApiResponse<ComprehensiveSearchResponse>> {
  return llmRequest({
    url: '/llm/comprehensive/search',
    method: 'post',
    data: params
  })
}

/**
 * 4. 获取诉求详情
 */
export function getComplaintDetail(
  serialNumber: string
): Promise<ApiResponse<ComplaintDetail>> {
  return llmRequest({
    url: `/llm/comprehensive/detail/${serialNumber}`,
    method: 'get'
  })
}


/**
 * 5. 综合查询大模型分析
 */
export function comprehensiveAnalyze(
  params: ComprehensiveAnalyzeRequest
): Promise<ApiResponse<AnalyzeResponse>> {
  return llmRequest({
    url: '/llm/comprehensive/analyze',
    method: 'post',
    data: params
  })
}
