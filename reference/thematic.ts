import { llmRequest } from '/@/utils/service';
import type {
  ApiResponse,
  DescribeProblemRequest,
  DescribeProblemResponse,
  ExtractKeywordsRequest,
  ExtractKeywordsResponse,
  SearchComplaintsRequest,
  SearchComplaintsResponse,
  GenerateReportRequest,
  GenerateReportResponse,
  ExportReportRequest,
  ExportReportResponse
} from './thematic-types';

/**
 * 专题分析LLM API接口
 */
export function useThematicAnalysisApi() {
  return {
    /**
     * 1. 专业问题分析
     * 对输入的问题标题进行专业分析，提供12345政务服务热线角度的概要分析
     * @param params 请求参数
     */
    describeProblem: (params: DescribeProblemRequest): Promise<ApiResponse<DescribeProblemResponse>> => {
      return llmRequest({
        url: '/llm/thematic-analysis/describe',
        method: 'post',
        data: params,
        timeout: 300000, // 5分钟超时
      });
    },

    /**
     * 2. 关键词提取
     * 根据输入的标题智能提取相关关键词，用于后续搜索
     * @param params 请求参数
     */
    extractKeywords: (params: ExtractKeywordsRequest): Promise<ApiResponse<ExtractKeywordsResponse>> => {
      return llmRequest({
        url: '/llm/thematic-analysis/keywords',
        method: 'post',
        data: params,
        timeout: 300000, // 5分钟超时
      });
    },

    /**
     * 3. 诉求数据搜索
     * 基于关键词和筛选条件搜索诉求数据，支持分页
     * @param params 请求参数
     */
    searchComplaints: (params: SearchComplaintsRequest): Promise<ApiResponse<SearchComplaintsResponse>> => {
      return llmRequest({
        url: '/llm/thematic-analysis/search',
        method: 'post',
        data: params,
        timeout: 300000, // 5分钟超时
      });
    },

    /**
     * 4. 生成分析报告
     * 基于搜索条件生成专业分析报告，包含主要问题、风险点、成因等
     * @param params 请求参数
     */
    generateReport: (params: GenerateReportRequest): Promise<ApiResponse<GenerateReportResponse>> => {
      return llmRequest({
        url: '/llm/thematic-analysis/report',
        method: 'post',
        data: params,
        timeout: 300000, // 5分钟超时，因为生成报告可能比较耗时
      });
    },

    /**
     * 5. 导出分析报告
     * 将生成的分析报告导出为PDF文件
     * @param params 请求参数
     */
    exportReport: (params: ExportReportRequest): Promise<ApiResponse<ExportReportResponse>> => {
      return llmRequest({
        url: '/llm/thematic-analysis/export',
        method: 'post',
        data: params,
        timeout: 300000, // 5分钟超时
      });
    },

    /**
     * 6. 文件下载
     * 下载导出的PDF文件
     * @param filename 文件名
     */
    downloadFile: (filename: string): Promise<Blob> => {
      return llmRequest({
        url: `/downloads/${filename}`,
        method: 'get',
        responseType: 'blob',
        timeout: 300000, // 5分钟超时
      });
    }
  };
}