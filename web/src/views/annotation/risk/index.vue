<template>
  <div class="risk-warning-container">
    <el-row :gutter="20" style="height: 100%;">
      <!-- 左侧诉求列表 -->
      <el-col :span="10">
        <el-card class="left-panel">
          <template #header>
            <div class="card-header">
              <span>风险标注件列表</span>
            </div>
          </template>

          <div class="complaint-list">
            <div v-if="isLoadingComplaints" class="loading-list">
              <el-icon class="is-loading"><Loading /></el-icon>
              <p>正在加载数据...</p>
            </div>
            <div v-else-if="error" class="error-list">
              <el-result
                icon="error"
                title="数据加载失败"
                :sub-title="error"
              >
                <template #extra>
                  <el-button type="primary" @click="loadLatestComplaints">重试</el-button>
                </template>
              </el-result>
            </div>
            <div v-else-if="filteredComplaints.length === 0" class="empty-list">
              <el-empty
                description="暂无风险标注件"
                :image-size="80"
              />
            </div>
            <div v-else>
              <div
                v-for="item in filteredComplaints"
                :key="item.complaint_id"
                class="complaint-item"
                :class="{ active: selectedComplaint?.complaint_id === item.complaint_id }"
                @click="selectComplaint(item)"
              >
                <div class="complaint-header">
                  <div class="complaint-no">{{ item.complaint_id }}</div>
                  <div class="complaint-title">{{ item.title }}</div>
                </div>
                <div class="complaint-content">{{ item.content }}</div>
                <div class="complaint-meta">
                  <span class="time">{{ item.accept_time }}</span>
                  <span class="status">{{ item.status }}</span>
                  <span class="area">{{ item.region }}</span>
                </div>
                <!-- 移除风险类别标签，模拟"待标注"外观 -->
              </div>
            </div>
          </div>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalComplaints"
            layout="prev, pager, next"
            @current-change="handlePageChange"
            style="margin-top: 16px; text-align: center;"
          />
        </el-card>
      </el-col>

      <!-- 右侧风险标注详情 -->
      <el-col :span="14">
        <el-card class="right-panel">
          <template #header>
            <span>风险标注详情</span>
          </template>

          <div v-if="!selectedComplaint" class="no-selection">
            <el-empty description="请从左侧选择一个诉求件查看风险标注详情" />
          </div>

          <div v-else class="assessment-content">
            <!-- 加载状态 -->
            <div v-if="isLoading" class="loading-content">
              <el-card class="loading-card" shadow="never">
                <div class="loading-wrapper">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  <span>正在加载详情...</span>
                </div>
              </el-card>
            </div>

            <!-- 风险标注详情面板 -->
            <template v-else>
              <el-card v-if="riskInfo.risk_category" class="risk-result-card" shadow="never">
                <template #header>
                  <span>风险标注结果</span>
                </template>

                <div class="risk-overview">
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="工单编号">
                      {{ complaintInfo.complaint_id }}
                    </el-descriptions-item>
                    <el-descriptions-item label="受理时间">
                      {{ complaintInfo.accept_time }}
                    </el-descriptions-item>
                    <el-descriptions-item label="风险类别" :span="2">
                      <el-tag :type="getRiskCategoryColor(riskInfo.risk_category)" size="large">
                        {{ riskInfo.risk_category }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="所属区域">
                      {{ complaintInfo.region }}
                    </el-descriptions-item>
                    <el-descriptions-item label="工单状态">
                      {{ complaintInfo.status }}
                    </el-descriptions-item>
                    <el-descriptions-item label="标注时间" :span="2">
                      {{ riskInfo.annotated_at }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>

                <el-divider />

                <div class="complaint-info">
                  <h4>诉求信息</h4>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="诉求标题">
                      {{ complaintInfo.title }}
                    </el-descriptions-item>
                    <el-descriptions-item label="诉求内容">
                      <div class="content-text">{{ complaintInfo.content }}</div>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>

                <el-divider />

                <div class="risk-details">
                  <h4>风险判定依据</h4>
                  <el-card class="reason-card" shadow="never">
                    <p class="risk-reason">{{ riskInfo.risk_reason }}</p>
                  </el-card>
                </div>
              </el-card>

              <!-- 无风险信息提示 -->
              <el-card v-if="!riskInfo.risk_category && !isLoading" class="no-risk-card" shadow="never">
                <el-empty description="未找到风险标注信息" :image-size="60" />
              </el-card>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="riskAnnotation">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import * as api from './api'
import type { ComplaintItem, RiskAnnotationDetail } from './types'

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const selectedComplaint = ref<ComplaintItem | null>(null)
const riskAnnotation = ref<RiskAnnotationDetail | null>(null)
const isLoading = ref(false)
const isLoadingComplaints = ref(false)
const complaints = ref<ComplaintItem[]>([])
const totalComplaints = ref(0)
const error = ref<string | null>(null)

// 计算属性
const filteredComplaints = computed(() => complaints.value)

// 获取当前选中投诉的风险标注信息
const riskInfo = computed(() => {
  if (!riskAnnotation.value?.risk) {
    return {}
  }

  const risk = riskAnnotation.value.risk
  return {
    risk_category: risk.risk_category,
    risk_reason: risk.risk_reason,
    annotated_at: risk.annotated_at
  }
})

// 获取诉求基本信息
const complaintInfo = computed(() => {
  if (!riskAnnotation.value?.complaint) {
    return {}
  }
  return riskAnnotation.value.complaint
})

// 风险类别颜色映射
const getRiskCategoryColor = (category: string) => {
  const colorMap: Record<string, string> = {
    '群体性事件风险': 'danger',
    '信访风险': 'warning',
    '舆情风险': 'primary',
    '安全风险': 'danger',
    '经济风险': 'warning',
    '社会稳定风险': 'danger'
  }
  return colorMap[category] || 'info'
}

// 加载已标注风险的诉求列表
const loadLatestComplaints = async () => {
  try {
    isLoadingComplaints.value = true
    error.value = null

    const result = await api.getRiskAnnotationList({
      page: currentPage.value,
      size: pageSize.value
    })

    if (result.code === 2000 && result.data) {
      complaints.value = result.data.data || []
      totalComplaints.value = result.data.total || 0
      ElMessage.success('数据加载成功')
    } else {
      throw new Error(result.msg || '数据加载失败')
    }
  } catch (err: any) {
    console.error('加载数据错误:', err)
    error.value = err.msg || err.message || '网络请求失败'
    ElMessage.error(`数据加载失败: ${error.value}`)
  } finally {
    isLoadingComplaints.value = false
  }
}

// 获取风险标注详情
const loadRiskDetail = async (complaintId: string) => {
  try {
    isLoading.value = true

    const result = await api.getRiskAnnotationDetail(complaintId)

    if (result.code === 2000 && result.data) {
      riskAnnotation.value = result.data
    } else {
      throw new Error(result.msg || '获取详情失败')
    }
  } catch (error: any) {
    console.error('获取详情错误:', error)
    ElMessage.error(`获取详情失败: ${error.message || error.msg || '未知错误'}`)
    riskAnnotation.value = null
  } finally {
    isLoading.value = false
  }
}

// 方法
const handlePageChange = (page: number) => {
  currentPage.value = page
  loadLatestComplaints()
  // 切换页面时清空选择
  selectedComplaint.value = null
  riskAnnotation.value = null
}

const selectComplaint = (complaint: ComplaintItem) => {
  selectedComplaint.value = complaint
  // 选中诉求后，加载风险标注详情
  if (complaint?.complaint_id) {
    loadRiskDetail(complaint.complaint_id)
  } else {
    riskAnnotation.value = null
  }
}

onMounted(async () => {
  // 页面加载时先加载列表数据
  await loadLatestComplaints()
})
</script>

<style scoped lang="scss">
.risk-warning-container {
  padding: 20px;
  height: calc(100vh - 120px);

  .left-panel, .right-panel {
    height: 100%;

    :deep(.el-card__body) {
      padding: 16px;
      height: calc(100% - 57px);
      overflow: hidden;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .complaint-list {
    height: calc(100% - 60px);
    overflow-y: auto;

    .empty-list, .error-list, .loading-list {
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
    }

    .complaint-item {
      padding: 12px;
      border: 1px solid var(--el-border-color-lighter);
      border-radius: 6px;
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        border-color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
      }

      &.active {
        border-color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-8);
        box-shadow: 0 2px 4px var(--el-color-primary-light-5);
      }

      .complaint-header {
        margin-bottom: 6px;

        .complaint-no {
          font-size: 11px;
          color: var(--el-color-primary);
          font-weight: 500;
          margin-bottom: 4px;
        }

        .complaint-title {
          font-weight: 600;
          color: var(--el-text-color-primary);
          font-size: 14px;
        }
      }

      .complaint-content {
        color: var(--el-text-color-regular);
        font-size: 12px;
        line-height: 1.4;
        margin-bottom: 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
      }

      .complaint-meta {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: var(--el-text-color-placeholder);
        margin-bottom: 6px;

        .time {
          color: var(--el-color-info);
        }

        .area {
          color: var(--el-color-success);
        }
      }
    }
  }

  .assessment-content {
    height: 100%;
    overflow-y: auto;

    .loading-card {
      .loading-wrapper {
        text-align: center;
        padding: 40px 20px;

        .el-icon {
          font-size: 32px;
          color: var(--el-color-primary);
          margin-bottom: 12px;
        }

        span {
          display: block;
          color: var(--el-text-color-regular);
          font-size: 14px;
        }
      }
    }

    .risk-result-card {
      margin-bottom: 16px;

      .risk-overview {
        margin-bottom: 16px;
      }

      .complaint-info,
      .risk-details {
        h4 {
          margin: 0 0 12px 0;
          color: var(--el-text-color-primary);
          font-size: 16px;
        }
      }

      .content-text {
        line-height: 1.6;
        max-height: 200px;
        overflow-y: auto;
      }

      .reason-card {
        background-color: var(--el-fill-color-extra-light);

        .risk-reason {
          margin: 0;
          line-height: 1.6;
          color: var(--el-text-color-regular);
        }
      }
    }

    .no-risk-card {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 300px;
    }
  }

  .no-selection {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
