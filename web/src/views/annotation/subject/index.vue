<template>
  <div class="subject-annotation-container">
    <el-row :gutter="20" style="height: 100%;">
      <!-- 左侧诉求列表 -->
      <el-col :span="10">
        <el-card class="left-panel">
          <template #header>
            <div class="card-header">
              <span>主体标注件列表</span>
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
                description="暂无主体标注件"
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

      <!-- 右侧主体标注详情 -->
      <el-col :span="14">
        <el-card class="right-panel">
          <template #header>
            <span>主体标注详情</span>
          </template>

          <div v-if="!selectedComplaint" class="no-selection">
            <el-empty description="请从左侧选择一个诉求件查看主体标注详情" />
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

            <!-- 主体标注详情面板 -->
            <template v-else>
              <el-card v-if="subjectInfo.subject_name" class="subject-result-card" shadow="never">
                <template #header>
                  <span>实体识别结果</span>
                </template>

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

                <div class="subject-details">
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="被投诉主体" :span="2">
                      <el-tag type="primary" size="large">{{ subjectInfo.subject_name }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="主体类型" :span="2">
                      <el-tag :type="subjectInfo.subject_type === '商业机构' ? 'primary' : 'success'">
                        {{ subjectInfo.subject_type }}
                      </el-tag>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-card>

              <!-- 商业机构详细标注面板 -->
              <el-card v-if="subjectInfo.industry || subjectInfo.scale" class="commercial-detail-card" shadow="never">
                <template #header>
                  <span>商业机构标注详情</span>
                </template>

                <el-descriptions :column="2" border>
                  <el-descriptions-item label="行业类型" v-if="subjectInfo.industry">
                    <el-tag type="primary">{{ subjectInfo.industry }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="企业规模" v-if="subjectInfo.scale">
                    <el-tag type="success">{{ subjectInfo.scale }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="投诉性质" v-if="subjectInfo.complaint_nature">
                    <el-tag type="warning">{{ subjectInfo.complaint_nature }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="经营形式" v-if="subjectInfo.model">
                    <el-tag type="info">{{ subjectInfo.model }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </el-card>

              <!-- 无主体信息提示 -->
              <el-card v-if="!subjectInfo.subject_name && !isLoading" class="no-subject-card" shadow="never">
                <el-empty description="未找到主体标注信息" :image-size="60" />
              </el-card>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="subjectAnnotation">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import * as api from './api'
import type { ComplaintItem, SubjectAnnotationDetail } from './types'

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const selectedComplaint = ref<ComplaintItem | null>(null)
const subjectAnnotation = ref<SubjectAnnotationDetail | null>(null)
const isLoading = ref(false)
const isLoadingComplaints = ref(false)
const complaints = ref<ComplaintItem[]>([])
const totalComplaints = ref(0)
const error = ref<string | null>(null)

// 计算属性
const filteredComplaints = computed(() => complaints.value)

// 获取当前选中投诉的主体标注信息
const subjectInfo = computed(() => {
  if (!subjectAnnotation.value?.subject) {
    return {}
  }

  const subject = subjectAnnotation.value.subject
  return {
    subject_name: subject.subject_name,
    subject_type: subject.subject_type,
    industry: subject.industry,
    scale: subject.scale,
    complaint_nature: subject.complaint_nature,
    model: subject.model,
    annotated_at: subject.annotated_at
  }
})

// 获取诉求基本信息
const complaintInfo = computed(() => {
  if (!subjectAnnotation.value?.complaint) {
    return {}
  }
  return subjectAnnotation.value.complaint
})

// 加载已标注主体信息的诉求列表
const loadLatestComplaints = async () => {
  try {
    isLoadingComplaints.value = true
    error.value = null

    const result = await api.getSubjectAnnotationList({
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

// 获取主体标注详情
const loadSubjectDetail = async (complaintId: string) => {
  try {
    isLoading.value = true

    const result = await api.getSubjectAnnotationDetail(complaintId)

    if (result.code === 2000 && result.data) {
      subjectAnnotation.value = result.data
    } else {
      throw new Error(result.msg || '获取详情失败')
    }
  } catch (error: any) {
    console.error('获取详情错误:', error)
    ElMessage.error(`获取详情失败: ${error.message || error.msg || '未知错误'}`)
    subjectAnnotation.value = null
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
  subjectAnnotation.value = null
}

const selectComplaint = (complaint: ComplaintItem) => {
  selectedComplaint.value = complaint
  // 选中诉求后，加载主体标注详情
  if (complaint?.complaint_id) {
    loadSubjectDetail(complaint.complaint_id)
  } else {
    subjectAnnotation.value = null
  }
}

onMounted(async () => {
  // 页面加载时先加载列表数据
  await loadLatestComplaints()
})
</script>

<style scoped lang="scss">
.subject-annotation-container {
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

    .subject-result-card {
      margin-bottom: 16px;

      .complaint-info {
        h4 {
          margin: 0 0 12px 0;
          color: var(--el-text-color-primary);
          font-size: 16px;
        }
      }

      .subject-details {
        margin-top: 16px;
      }

      .content-text {
        line-height: 1.6;
        max-height: 200px;
        overflow-y: auto;
      }
    }

    .commercial-detail-card {
      margin-bottom: 16px;
    }

    .no-subject-card {
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
