<template>
  <fs-page class="group-event-container">
    <fs-crud ref="crudRef" v-bind="crudBinding" />

    <!-- 工单详情弹窗 -->
    <ComplaintDetail ref="complaintDetailRef" />

    <!-- 关联工单列表对话框 -->
    <RelatedComplaintsDialog
      ref="relatedComplaintsDialogRef"
      :complaint-detail-ref="complaintDetailRef"
    />
  </fs-page>
</template>

<script lang="ts" setup name="groupEvent">
import { onMounted, ref, defineAsyncComponent } from 'vue'
import { useExpose, useCrud } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

// 工单详情组件
const ComplaintDetail = defineAsyncComponent(
  () => import('/@/components/ComplaintDetail/index.vue')
)

// 关联工单对话框组件
const RelatedComplaintsDialog = defineAsyncComponent(
  () => import('./RelatedComplaintsDialog.vue')
)

const complaintDetailRef = ref()
const relatedComplaintsDialogRef = ref()

// crud组件的ref
const crudRef = ref()
// crud 配置的ref
const crudBinding = ref()
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding })

// crud配置
const { crudOptions } = createCrudOptions({
  crudExpose,
  context: {},
  complaintDetailRef,
  relatedComplaintsDialogRef
})

// 初始化crud配置
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions })

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh()
})
</script>

<style scoped lang="scss">
.group-event-container {
  :deep(.fs-crud) {
    .el-card {
      border: none;
      box-shadow: none;
    }
  }
}
</style>
