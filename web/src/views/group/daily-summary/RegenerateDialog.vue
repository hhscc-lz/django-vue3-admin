<template>
  <el-dialog
    v-model="visible"
    :title="`重新生成摘要 - ${currentDate}`"
    width="800px"
    top="5vh"
    destroy-on-close
  >
    <div v-loading="loading" class="regenerate-content">
      <template v-if="regeneratedData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日期">
            {{ regeneratedData.summary_date }}
          </el-descriptions-item>
          <el-descriptions-item label="事件数量">
            <el-tag type="warning">{{ regeneratedData.event_count }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="标题" :span="2">
            {{ regeneratedData.title }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">日报内容</el-divider>

        <div class="summary-content">
          {{ regeneratedData.content }}
        </div>

        <el-divider content-position="left">关联事件ID</el-divider>

        <div class="event-ids">
          <el-tag
            v-for="id in regeneratedData.event_ids"
            :key="id"
            type="info"
            class="event-id-tag"
          >
            {{ id }}
          </el-tag>
        </div>
      </template>

      <el-empty v-else-if="!loading" description="点击下方按钮重新生成摘要" />
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="primary" :loading="loading" @click="handleRegenerate">
        {{ regeneratedData ? '再次生成' : '开始生成' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Regenerate } from './api'
import type { RegeneratedSummary } from './types'

const visible = ref(false)
const loading = ref(false)
const currentDate = ref('')
const regeneratedData = ref<RegeneratedSummary | null>(null)

const open = (date: string) => {
  currentDate.value = date
  regeneratedData.value = null
  visible.value = true
}

const handleRegenerate = async () => {
  if (!currentDate.value) return

  loading.value = true
  try {
    const res = await Regenerate(currentDate.value)
    regeneratedData.value = res
    ElMessage.success('摘要重新生成成功')
  } catch (error: any) {
    ElMessage.error(error?.message || '生成失败，请重试')
  } finally {
    loading.value = false
  }
}

defineExpose({ open })
</script>

<style scoped lang="scss">
.regenerate-content {
  min-height: 200px;
}

.summary-content {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
}

.event-ids {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.event-id-tag {
  cursor: default;
}
</style>
