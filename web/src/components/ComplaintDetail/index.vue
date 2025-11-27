<template>
  <el-dialog
    v-model="visible"
    title="工单详情"
    width="1200px"
    top="5vh"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-skeleton :loading="loading" animated>
      <template #default>
        <div v-if="detail" class="complaint-detail">
          <!-- 基础信息 -->
          <el-divider content-position="left">基础信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="工单编号">{{ detail.id }}</el-descriptions-item>
            <el-descriptions-item label="诉求标题">{{ detail.title || '-' }}</el-descriptions-item>
            <el-descriptions-item label="诉求人姓名">{{ detail.complainant_name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="诉求人手机号">{{ detail.complainant_phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="所属区域">{{ detail.region || '-' }}</el-descriptions-item>
            <el-descriptions-item label="来源渠道">{{ detail.source_channel || '-' }}</el-descriptions-item>
            <el-descriptions-item :span="2" label="诉求内容">
              <div class="content-text">{{ detail.content || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 分类信息 -->
          <el-divider content-position="left">分类信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="工单类型">{{ detail.order_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="诉求类型">{{ detail.complaint_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="一级分类">{{ detail.category_level1 || '-' }}</el-descriptions-item>
            <el-descriptions-item label="二级分类">{{ detail.category_level2 || '-' }}</el-descriptions-item>
            <el-descriptions-item label="三级分类">{{ detail.category_level3 || '-' }}</el-descriptions-item>
            <el-descriptions-item label="四级分类">{{ detail.category_level4 || '-' }}</el-descriptions-item>
          </el-descriptions>

          <!-- 流程信息 -->
          <el-divider content-position="left">流程信息</el-divider>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="工单状态">{{ detail.status || '-' }}</el-descriptions-item>
            <el-descriptions-item label="处理部门">{{ detail.handle_department || '-' }}</el-descriptions-item>
            <el-descriptions-item label="受理时间">{{ detail.accept_time || '-' }}</el-descriptions-item>
            <el-descriptions-item label="办结时间">{{ detail.complete_time || '-' }}</el-descriptions-item>
            <el-descriptions-item label="回复时间">{{ detail.reply_time || '-' }}</el-descriptions-item>
            <el-descriptions-item label="回访结果">{{ detail.callback_result || '-' }}</el-descriptions-item>
            <el-descriptions-item :span="2" label="回复诉求人">
              <div class="content-text">{{ detail.reply_person || '-' }}</div>
            </el-descriptions-item>
          </el-descriptions>

          <!-- 统计信息 -->
          <el-divider content-position="left">统计信息</el-divider>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="催单次数">{{ detail.urge_count ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="补单次数">{{ detail.supplement_count ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="重复次数">{{ detail.repeat_count ?? '-' }}</el-descriptions-item>
          </el-descriptions>

          <!-- 风险信息 -->
          <template v-if="detail.risk_info">
            <el-divider content-position="left">风险信息</el-divider>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="是否风险">
                <el-tag :type="detail.risk_info.is_risk ? 'danger' : 'success'">
                  {{ detail.risk_info.is_risk ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="风险类别">{{ detail.risk_info.risk_category || '-' }}</el-descriptions-item>
              <el-descriptions-item label="标注时间">{{ detail.risk_info.created_at || '-' }}</el-descriptions-item>
              <el-descriptions-item :span="2" label="判定原因">
                <div class="content-text">{{ detail.risk_info.risk_reason || '-' }}</div>
              </el-descriptions-item>
            </el-descriptions>
          </template>
        </div>
      </template>
    </el-skeleton>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup name="ComplaintDetail">
import { ref } from 'vue'
import { GetFullDetail } from './api'
import type { ComplaintFullDetail } from './types'

// 弹窗显示状态
const visible = ref(false)
// 加载状态
const loading = ref(false)
// 工单详情数据
const detail = ref<ComplaintFullDetail | null>(null)

/**
 * 打开详情弹窗
 * @param complaintId 工单编号
 */
const open = async (complaintId: string) => {
  visible.value = true
  loading.value = true
  detail.value = null

  try {
    const response = await GetFullDetail(complaintId)
    // 从响应对象中提取 data 字段
    detail.value = response.data || response
  } catch (error) {
    console.error('获取工单详情失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 关闭详情弹窗
 */
const close = () => {
  visible.value = false
}

// 暴露方法给父组件
defineExpose({
  open,
  close
})
</script>

<style lang="scss" scoped>
.complaint-detail {
  .content-text {
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 200px;
    overflow-y: auto;
  }

  .el-divider {
    margin-top: 24px;
    margin-bottom: 16px;

    &:first-child {
      margin-top: 0;
    }
  }
}
</style>
