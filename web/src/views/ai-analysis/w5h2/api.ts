/**
 * 5W2H 分析 API 接口
 */
import { llmRequest } from '/@/utils/service'
import type {
  ApiResponse,
  SearchRequest,
  SearchResponse,
  ComplaintDetail,
  AnalyzeRequest,
  AnalyzeResponse,
  ExportReportRequest
} from './types'

/**
 * 1. 搜索诉求数据
 * 根据查询条件搜索诉求列表
 */
export function searchComplaints(
  params: SearchRequest
): Promise<ApiResponse<SearchResponse>> {
  return llmRequest({
    url: '/llm/w5h2/search',
    method: 'post',
    data: params
  })
}

/**
 * 2. 获取诉求详情
 * 获取单条诉求的完整详情数据
 */
export function getComplaintDetail(
  serialNumber: string
): Promise<ApiResponse<ComplaintDetail>> {
  return llmRequest({
    url: `/llm/w5h2/detail/${serialNumber}`,
    method: 'get'
  })
}

/**
 * 3. 大模型分析
 * 基于查询条件生成AI分析报告
 */
export function analyzeComplaints(
  params: AnalyzeRequest
): Promise<ApiResponse<AnalyzeResponse>> {
  return llmRequest({
    url: '/llm/w5h2/analyze',
    method: 'post',
    data: params
  })
}

/**
 * 4. 导出分析报告
 * 将分析报告导出为Word文档
 */
export function exportReport(
  params: ExportReportRequest
): Promise<Blob> {
  return llmRequest({
    url: '/llm/w5h2/export',
    method: 'post',
    data: params,
    responseType: 'blob'
  })
}
