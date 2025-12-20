<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="1400px"
    top="5vh"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-table
      v-loading="loading"
      :data="complaints"
      border
      stripe
      style="width: 100%"
    >
      <el-table-column prop="complaint_id" label="工单编号" width="150" />
      <el-table-column prop="complaint_detail.title" label="诉求标题" width="250" show-overflow-tooltip />
      <el-table-column prop="complaint_detail.region" label="区域" width="120" />
      <el-table-column prop="complaint_detail.category_level1" label="一级分类" width="120" />
      <el-table-column prop="complaint_detail.category_level2" label="二级分类" width="120" />
      <el-table-column prop="complaint_detail.status" label="状态" width="100" />
      <el-table-column prop="complaint_detail.accept_time" label="受理时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.complaint_detail.accept_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            @click="viewComplaintDetail(row.complaint_id)"
          >
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.limit"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 16px; justify-content: flex-end"
    />

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup name="RelatedComplaintsDialog">
import { ref, computed } from 'vue'
import { GetRelatedComplaints } from './api'
import type { GroupEventComplaint } from './types'
import dayjs from 'dayjs'

// 弹窗显示状态
const visible = ref(false)
// 加载状态
const loading = ref(false)
// 当前事件ID
const currentEventId = ref<number | null>(null)
// 当前事件标题
const currentEventTitle = ref<string>('')
// 关联工单列表
const complaints = ref<GroupEventComplaint[]>([])
// 分页配置
const pagination = ref({
  page: 1,
  limit: 20,
  total: 0
})

// 对话框标题
const dialogTitle = computed(() => {
  return `关联工单列表 - ${currentEventTitle.value}`
})

/**
 * 打开对话框
 */
const open = async (eventId: number, eventTitle: string) => {
  currentEventId.value = eventId
  currentEventTitle.value = eventTitle
  visible.value = true

  // 重置分页
  pagination.value.page = 1

  // 加载数据
  await loadComplaints()
}

/**
 * 加载关联工单数据
 */
const loadComplaints = async () => {
  if (!currentEventId.value) return

  loading.value = true
  try {
    const response = await GetRelatedComplaints(currentEventId.value, {
      page: pagination.value.page,
      limit: pagination.value.limit
    })

    complaints.value = response.data || []
    pagination.value.total = response.total || 0
  } catch (error) {
    console.error('加载关联工单失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 分页大小改变
 */
const handleSizeChange = (size: number) => {
  pagination.value.limit = size
  pagination.value.page = 1
  loadComplaints()
}

/**
 * 当前页改变
 */
const handleCurrentChange = (page: number) => {
  pagination.value.page = page
  loadComplaints()
}

/**
 * 格式化时间
 */
const formatDateTime = (datetime: string | null) => {
  return datetime ? dayjs(datetime).format('YYYY-MM-DD HH:mm:ss') : '-'
}

/**
 * 查看工单详情
 */
const viewComplaintDetail = (complaintId: string) => {
  // 这里可以打开工单详情弹窗
  // 需要传入 complaintDetailRef
  console.log('查看工单详情:', complaintId)
}

// 暴露方法给父组件
defineExpose({
  open
})
</script>

<style scoped lang="scss">
:deep(.el-pagination) {
  display: flex;
}
</style>
