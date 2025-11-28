<template>
  <div class="spatial-annotation-container">
    <el-row :gutter="20" style="height: 100%;">
      <!-- 左侧诉求列表 -->
      <el-col :span="10">
        <el-card class="left-panel">
          <template #header>
            <div class="card-header">
              <span>空间标注件列表</span>
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
                description="暂无空间标注件"
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

      <!-- 右侧空间标注详情 -->
      <el-col :span="14">
        <el-card class="right-panel">
          <template #header>
            <span>空间标注详情</span>
          </template>

          <div v-if="!selectedComplaint" class="no-selection">
            <el-empty description="请从左侧选择一个诉求件查看空间标注详情" />
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

            <!-- 空间标注详情面板 -->
            <template v-else>
              <el-card v-if="spatialInfo.address" class="spatial-result-card" shadow="never">
                <template #header>
                  <span>空间标注结果</span>
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

                <div class="spatial-details">
                  <h4>空间定位信息</h4>
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="诉求地址" :span="2">
                      <el-tag type="primary" size="large">{{ spatialInfo.address }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="地址类型">
                      {{ spatialInfo.address_type || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="区县">
                      {{ spatialInfo.district || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="街道">
                      {{ spatialInfo.street || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="小区">
                      {{ spatialInfo.community || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="经度">
                      {{ spatialInfo.longitude !== null ? spatialInfo.longitude : '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="纬度">
                      {{ spatialInfo.latitude !== null ? spatialInfo.latitude : '-' }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-card>

              <!-- 百度地图 -->
              <el-card v-if="spatialInfo.longitude !== null && spatialInfo.latitude !== null" class="map-card" shadow="never">
                <template #header>
                  <div class="map-header">
                    <span>地理位置 ({{ spatialInfo.longitude?.toFixed(6) }}, {{ spatialInfo.latitude?.toFixed(6) }})</span>
                  </div>
                </template>
                <div id="baiduMap" class="baidu-map"></div>
              </el-card>

              <!-- 无空间标注信息提示 -->
              <el-card v-if="!spatialInfo.address && !isLoading" class="no-spatial-card" shadow="never">
                <el-empty description="未找到空间标注信息" :image-size="60" />
              </el-card>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="spatialAnnotation">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import * as api from './api'
import type { ComplaintItem, SpatialAnnotationDetail } from './types'

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const selectedComplaint = ref<ComplaintItem | null>(null)
const spatialAnnotation = ref<SpatialAnnotationDetail | null>(null)
const mapInstance = ref(null)
const isLoading = ref(false)
const isLoadingComplaints = ref(false)
const complaints = ref<ComplaintItem[]>([])
const totalComplaints = ref(0)
const error = ref<string | null>(null)

// 计算属性
const filteredComplaints = computed(() => complaints.value)

// 获取当前选中投诉的空间标注信息
const spatialInfo = computed(() => {
  if (!spatialAnnotation.value?.spatial) {
    return {}
  }

  const spatial = spatialAnnotation.value.spatial
  return {
    address: spatial.address,
    address_type: spatial.address_type,
    longitude: spatial.longitude,
    latitude: spatial.latitude,
    district: spatial.district,
    street: spatial.street,
    community: spatial.community,
    annotated_at: spatial.annotated_at
  }
})

// 获取诉求基本信息
const complaintInfo = computed(() => {
  if (!spatialAnnotation.value?.complaint) {
    return {}
  }
  return spatialAnnotation.value.complaint
})

// 加载已标注空间信息的诉求列表
const loadLatestComplaints = async () => {
  try {
    isLoadingComplaints.value = true
    error.value = null

    const result = await api.getSpatialAnnotationList({
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

// 获取空间标注详情
const loadSpatialDetail = async (complaintId: string) => {
  try {
    isLoading.value = true

    const result = await api.getSpatialAnnotationDetail(complaintId)

    if (result.code === 2000 && result.data) {
      spatialAnnotation.value = result.data
    } else {
      throw new Error(result.msg || '获取详情失败')
    }
  } catch (error: any) {
    console.error('获取详情错误:', error)
    ElMessage.error(`获取详情失败: ${error.message || error.msg || '未知错误'}`)
    spatialAnnotation.value = null
  } finally {
    isLoading.value = false
  }
}

// 百度地图初始化 (使用GL版本API)
const initBaiduMap = () => {
  if (!spatialInfo.value.longitude || !spatialInfo.value.latitude) return

  const { longitude, latitude } = spatialInfo.value

  // 检查百度地图API是否已加载
  if (typeof window.BMapGL === 'undefined') {
    console.warn('百度地图API GL版本未加载，请确认index.html中已正确引入百度地图API')
    const mapElement = document.getElementById('baiduMap')
    if (mapElement) {
      mapElement.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #909399;">百度地图API未加载，请配置有效的API Key</div>'
    }
    return
  }

  try {
    // 清除之前的地图实例
    if (mapInstance.value) {
      mapInstance.value = null
    }

    // 创建地图实例 (GL版本)
    const map = new window.BMapGL.Map("baiduMap")
    mapInstance.value = map

    // 创建点坐标
    const point = new window.BMapGL.Point(longitude, latitude)

    // 初始化地图，设置中心点坐标和地图级别
    map.centerAndZoom(point, 15)

    // 创建标注
    const marker = new window.BMapGL.Marker(point)
    map.addOverlay(marker)

    // 添加地图类型控件
    map.addControl(new window.BMapGL.MapTypeControl({
      mapTypes: [window.BMAP_NORMAL_MAP, window.BMAP_HYBRID_MAP]
    }))

    // 添加比例尺控件
    map.addControl(new window.BMapGL.ScaleControl())

    // 添加缩放控件
    map.addControl(new window.BMapGL.ZoomControl())

    // 创建信息窗口
    const infoWindow = new window.BMapGL.InfoWindow(
      `<div style="padding: 12px; line-height: 1.5; font-family: 'Microsoft YaHei', Arial, sans-serif;">
        <h4 style="margin: 0 0 8px 0; color: #303133; font-size: 14px;">${selectedComplaint.value?.title || ''}</h4>
        <p style="margin: 0 0 4px 0; color: #606266; font-size: 12px;">编号：${selectedComplaint.value?.complaint_id || ''}</p>
        <p style="margin: 0 0 4px 0; color: #606266; font-size: 12px;">地址：${spatialInfo.value.address}</p>
        ${spatialInfo.value.community ? `<p style="margin: 0; color: #606266; font-size: 12px;">小区：${spatialInfo.value.community}</p>` : ''}
      </div>`,
      { width: 300, height: 140 }
    )

    // 点击标记显示信息窗口
    marker.addEventListener('click', () => {
      map.openInfoWindow(infoWindow, point)
    })

    // 开启鼠标滚轮缩放
    map.enableScrollWheelZoom(true)

    // 开启地图拖拽
    map.enableDragging(true)

    // 开启双击放大
    map.enableDoubleClickZoom(true)

    // 开启键盘操作
    map.enableKeyboard(true)

    console.log('百度地图GL版本初始化成功，坐标：', longitude, latitude)
  } catch (error) {
    console.error('百度地图初始化失败：', error)
    const mapElement = document.getElementById('baiduMap')
    if (mapElement) {
      mapElement.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #f56c6c;">地图加载失败，请检查网络连接或API Key</div>'
    }
  }
}

// 监听空间标注结果变化，自动初始化地图
watch(() => spatialAnnotation.value, () => {
  if (spatialAnnotation.value && spatialInfo.value.longitude !== null && spatialInfo.value.latitude !== null) {
    nextTick(() => {
      initBaiduMap()
    })
  }
})

// 方法
const handlePageChange = (page: number) => {
  currentPage.value = page
  loadLatestComplaints()
  // 切换页面时清空选择
  selectedComplaint.value = null
  spatialAnnotation.value = null
}

const selectComplaint = (complaint: ComplaintItem) => {
  selectedComplaint.value = complaint
  // 选中诉求后，加载空间标注详情
  if (complaint?.complaint_id) {
    loadSpatialDetail(complaint.complaint_id)
  } else {
    spatialAnnotation.value = null
  }
}

onMounted(async () => {
  // 页面加载时先加载列表数据
  await loadLatestComplaints()
})
</script>

<style scoped lang="scss">
.spatial-annotation-container {
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

    .spatial-result-card {
      margin-bottom: 16px;

      .complaint-info,
      .spatial-details {
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
    }

    .map-card {
      margin-bottom: 16px;

      .map-header {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .baidu-map {
        width: 100%;
        height: 400px;
        background-color: var(--el-fill-color-light);
        border-radius: 4px;
        position: relative;

        &:empty::before {
          content: '百度地图加载中...';
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: var(--el-text-color-placeholder);
        }
      }
    }

    .no-spatial-card {
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
