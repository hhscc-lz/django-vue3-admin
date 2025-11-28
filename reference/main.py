import logging
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from models import (
    ExplainRequest, ExplainResponse,
    KeywordRequest, KeywordResponse,
    SearchRequest, SearchResponse,
    ReportRequest, ReportResponse,
    ExportRequest, ExportResponse,
    ResponseModel
)
from services.llm_service import get_llm_service
from services.es_service import get_es_client
from services.export_service import get_export_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="12345专题分析服务",
    description="基于大模型的12345诉求数据专题分析API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 内存存储报告内容
_report_storage = {}

# 创建API路由器
llm_router = APIRouter(prefix="/llm")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "12345专题分析服务", "status": "running"}


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查ES连接
        es_client = get_es_client()
        es_healthy = es_client.health_check()

        return {
            "status": "healthy" if es_healthy else "unhealthy",
            "elasticsearch": es_healthy,
            "timestamp": "2024-01-01 00:00:00"  # 可以替换为实际时间
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@llm_router.post("/thematic-analysis/describe", response_model=ResponseModel[ExplainResponse])
async def get_explanation(request: ExplainRequest):
    """
    获取专业问题分析

    Args:
        request: 包含需要分析的问题类型

    Returns:
        ResponseModel[ExplainResponse]: 专业问题分析结果
    """
    try:
        llm_service = get_llm_service()
        explanation = llm_service.get_professional_explanation(request.title)

        result = ExplainResponse(
            title=request.title,
            explanation=explanation
        )

        return ResponseModel(
            code=2000,
            msg="success",
            data=result
        )
    except Exception as e:
        logger.error(f"专业问题分析失败: {e}")
        return ResponseModel(
            code=5000,
            msg=f"专业问题分析失败: {str(e)}",
            data=None
        )


@llm_router.post("/thematic-analysis/keywords", response_model=ResponseModel[KeywordResponse])
async def extract_keywords(request: KeywordRequest):
    """
    提取相关关键词

    Args:
        request: 包含需要提取关键词的词汇

    Returns:
        ResponseModel[KeywordResponse]: 提取的关键词列表
    """
    try:
        llm_service = get_llm_service()
        keywords = llm_service.extract_keywords(request.title)

        result = KeywordResponse(
            title=request.title,
            keywords=keywords
        )

        return ResponseModel(
            code=2000,
            msg="success",
            data=result
        )
    except Exception as e:
        logger.error(f"关键词提取失败: {e}")
        return ResponseModel(
            code=5000,
            msg=f"关键词提取失败: {str(e)}",
            data=None
        )


@llm_router.post("/thematic-analysis/search", response_model=ResponseModel[SearchResponse])
async def search_requests(request: SearchRequest):
    """
    基于关键词搜索诉求数据

    Args:
        request: 包含关键词列表和分页参数

    Returns:
        ResponseModel[SearchResponse]: 搜索结果
    """
    try:
        es_client = get_es_client()
        result = es_client.search_by_keywords(request)

        return ResponseModel(
            code=2000,
            msg="success",
            data=result,
            count=result.total
        )
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        return ResponseModel(
            code=5000,
            msg=f"搜索失败: {str(e)}",
            data=None
        )


@llm_router.post("/thematic-analysis/report", response_model=ResponseModel[ReportResponse])
async def generate_report(request: ReportRequest):
    """
    生成分析报告

    Args:
        request: 包含查询条件和分析参数

    Returns:
        ResponseModel[ReportResponse]: 分析报告结果
    """
    try:
        # 验证关键词
        if not request.keywords:
            return ResponseModel(
                code=4000,
                msg="关键词列表不能为空",
                data=None
            )

        # 使用scroll查询获取所有匹配的诉求数据（最大2000条）
        es_client = get_es_client()
        requests_data = es_client.scroll_search_for_report(request, max_count=2000)

        if not requests_data:
            return ResponseModel(
                code=4004,
                msg="根据查询条件未找到匹配的诉求数据",
                data=None
            )

        logger.info(f"找到 {len(requests_data)} 条匹配的诉求数据用于生成报告")

        # 生成分析报告
        llm_service = get_llm_service()
        report_content = llm_service.generate_analysis_report(
            title=request.title,
            requests_data=requests_data
        )

        # 生成报告ID和时间
        import hashlib
        from datetime import datetime

        # 基于查询条件和时间生成唯一ID
        query_hash = hashlib.md5(
            f"{request.keywords}_{request.start_time}_{request.end_time}_{request.handling_area}_{datetime.now()}".encode()
        ).hexdigest()[:12]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_id = f"report_{query_hash}"

        # 存储报告内容到内存
        _report_storage[report_id] = {
            "title": request.title,
            "content": report_content,
            "generated_at": current_time
        }

        result = ReportResponse(
            report_id=report_id,
            title=request.title,
            status="completed",
            content=report_content,
            data_count=len(requests_data),
            generated_at=current_time
        )

        return ResponseModel(
            code=2000,
            msg="success",
            data=result
        )

    except Exception as e:
        logger.error(f"生成分析报告失败: {e}")
        return ResponseModel(
            code=5000,
            msg=f"生成分析报告失败: {str(e)}",
            data=None
        )


@llm_router.post("/thematic-analysis/export", response_model=ResponseModel[ExportResponse])
async def export_report(request: ExportRequest):
    """
    导出分析报告为PDF

    Args:
        request: 包含要导出的报告ID和格式

    Returns:
        ResponseModel[ExportResponse]: 导出结果
    """
    try:
        # 检查报告是否存在
        if request.report_id not in _report_storage:
            return ResponseModel(
                code=4004,
                msg=f"报告 {request.report_id} 不存在",
                data=None
            )

        # 获取报告信息
        report_info = _report_storage[request.report_id]

        # 检查导出格式
        if request.format.lower() != "pdf":
            return ResponseModel(
                code=4000,
                msg="目前仅支持PDF格式导出",
                data=None
            )

        # 使用导出服务生成PDF
        export_service = get_export_service()
        export_result = export_service.export_report_to_pdf(
            report_id=request.report_id,
            title=report_info["title"],
            content=report_info["content"]
        )

        return ResponseModel(
            code=2000,
            msg="success",
            data=export_result
        )

    except Exception as e:
        logger.error(f"导出报告失败: {e}")
        return ResponseModel(
            code=5000,
            msg=f"导出报告失败: {str(e)}",
            data=None
        )


@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """
    下载导出的文件

    Args:
        filename: 文件名

    Returns:
        FileResponse: 文件下载响应
    """
    try:
        export_service = get_export_service()
        file_path = export_service.get_file_path(filename)

        # 检查文件是否存在
        import os
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"文件 {filename} 不存在"
            )

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf'
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件下载失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")


# 注册路由器
app.include_router(llm_router)


def main():
    """启动应用"""
    import uvicorn
    settings = get_settings()

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
