<template>
  <div class="topic-annotation-container">
    <el-row :gutter="20" style="height: 100%;">
      <!-- 左侧诉求列表 -->
      <el-col :span="10">
        <el-card class="left-panel">
          <template #header>
            <div class="card-header">
              <span>专题标注件列表</span>
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
                description="暂无专题标注件"
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

      <!-- 右侧专题标注详情 -->
      <el-col :span="14">
        <el-card class="right-panel">
          <template #header>
            <span>专题标注详情</span>
          </template>

          <div v-if="!selectedComplaint" class="no-selection">
            <el-empty description="请从左侧选择一个诉求件查看专题标注详情" />
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

            <!-- 专题标注详情面板 -->
            <template v-else>
              <el-card v-if="topicInfo.topic_name" class="topic-result-card" shadow="never">
                <template #header>
                  <span>专题分析结果</span>
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

                <div class="topic-details">
                  <h4>专题标注信息</h4>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="专题名称">
                      <el-tag type="primary" size="large">{{ topicInfo.topic_name }}</el-tag>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>

                <el-divider />

                <!-- 动态展示专题细分字段 -->
                <div v-if="topicFieldsArray.length > 0" class="topic-fields">
                  <h4>专题细分字段</h4>
                  <el-descriptions :column="2" border>
                    <el-descriptions-item
                      v-for="field in topicFieldsArray"
                      :key="field.key"
                      :label="formatFieldLabel(field.key)"
                    >
                      <el-tag type="success">{{ field.value }}</el-tag>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-card>

              <!-- 无专题信息提示 -->
              <el-card v-if="!topicInfo.topic_name && !isLoading" class="no-topic-card" shadow="never">
                <el-empty description="未找到专题标注信息" :image-size="60" />
              </el-card>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="topicAnnotation">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import * as api from './api'
import type { ComplaintItem, TopicAnnotationDetail } from './types'

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const selectedComplaint = ref<ComplaintItem | null>(null)
const topicAnnotation = ref<TopicAnnotationDetail | null>(null)
const isLoading = ref(false)
const isLoadingComplaints = ref(false)
const complaints = ref<ComplaintItem[]>([])
const totalComplaints = ref(0)
const error = ref<string | null>(null)

// 计算属性
const filteredComplaints = computed(() => complaints.value)

// 获取当前选中投诉的专题标注信息
const topicInfo = computed(() => {
  if (!topicAnnotation.value?.topic) {
    return {}
  }

  const topic = topicAnnotation.value.topic
  return {
    topic_name: topic.topic_name,
    topic_fields: topic.topic_fields,
    annotated_at: topic.annotated_at
  }
})

// 获取诉求基本信息
const complaintInfo = computed(() => {
  if (!topicAnnotation.value?.complaint) {
    return {}
  }
  return topicAnnotation.value.complaint
})

// 将JSON对象转换为数组便于遍历
const topicFieldsArray = computed(() => {
  const fields = topicInfo.value.topic_fields
  if (!fields || typeof fields !== 'object') {
    return []
  }

  return Object.entries(fields).map(([key, value]) => ({
    key,
    value: String(value)
  }))
})

// 字段名中文映射表（汇总所有专题的字段）
const fieldLabelMapping: Record<string, string> = {
  // 消费者权益专题
  'industry_type': '行业类型',
  'consumption_amount': '消费金额',
  'dispute_type': '纠纷类型',
  'safety_involved': '安全相关',
  'victim_scale': '受害规模',
  'is_emerging_industry': '是否新兴产业',

  // 物业管理专题
  'service_type': '服务类型',
  'problem_type': '问题类型',
  'facility_equipment': '设施设备',
  'fee_related': '收费相关',

  // 噪声污染专题
  'noise_source': '噪声源',
  'impact_degree': '影响程度',
  'time_characteristics': '时间特征',
  'affected_area': '影响范围',

  // 市容环卫专题
  'facility_category': '设施类别',
  'severity_level': '严重程度',
  'impact_scope': '影响范围',

  // 劳动权益专题
  'employer_type': '用工主体',
  'amount_involved': '涉及金额',
  'urgency_level': '紧急程度',
  'affected_workers': '涉及人数',

  // 市政设施专题
  'facility_type': '设施类型',
  'problem_nature': '问题性质',
  'facility_condition': '设施状态',

  // 供热问题反馈专题
  'temperature_low': '温度不达标',
  'no_heating': '不供暖',
  'leakage': '漏水问题',
  'pipe_damage': '管道损坏',
  'fee_dispute': '费用纠纷',
  'service_attitude': '服务态度',
  'equipment_failure': '设备故障',

  // 土地管理专题
  'land_type': '土地类型',
  'scale_involved': '涉及规模'
}

// 格式化字段标签（优先使用映射表，否则转换为标题格式）
const formatFieldLabel = (key: string): string => {
  // 优先使用映射表
  if (fieldLabelMapping[key]) {
    return fieldLabelMapping[key]
  }

  // 如果映射表中没有，则将snake_case转换为标题格式
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// 加载已标注专题信息的诉求列表
const loadLatestComplaints = async () => {
  try {
    isLoadingComplaints.value = true
    error.value = null

    const result = await api.getTopicAnnotationList({
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

// 获取专题标注详情
const loadTopicDetail = async (complaintId: string) => {
  try {
    isLoading.value = true

    const result = await api.getTopicAnnotationDetail(complaintId)

    if (result.code === 2000 && result.data) {
      topicAnnotation.value = result.data
    } else {
      throw new Error(result.msg || '获取详情失败')
    }
  } catch (error: any) {
    console.error('获取详情错误:', error)
    ElMessage.error(`获取详情失败: ${error.message || error.msg || '未知错误'}`)
    topicAnnotation.value = null
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
  topicAnnotation.value = null
}

const selectComplaint = (complaint: ComplaintItem) => {
  selectedComplaint.value = complaint
  // 选中诉求后，加载专题标注详情
  if (complaint?.complaint_id) {
    loadTopicDetail(complaint.complaint_id)
  } else {
    topicAnnotation.value = null
  }
}

onMounted(async () => {
  // 页面加载时先加载列表数据
  await loadLatestComplaints()
})
</script>

<style scoped lang="scss">
.topic-annotation-container {
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

    .topic-result-card {
      margin-bottom: 16px;

      .complaint-info,
      .topic-details,
      .topic-fields {
        h4 {
          margin: 0 0 12px 0;
          color: var(--el-text-color-primary);
          font-size: 16px;
        }
      }

      .topic-fields {
        margin-top: 16px;
      }

      .content-text {
        line-height: 1.6;
        max-height: 200px;
        overflow-y: auto;
      }
    }

    .no-topic-card {
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
