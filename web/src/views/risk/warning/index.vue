<template>
  <fs-page class="risk-warning-container">
    <fs-crud ref="crudRef" v-bind="crudBinding" />
    <!-- 工单详情弹窗 -->
    <ComplaintDetail ref="complaintDetailRef" />
  </fs-page>
</template>

<script lang="ts" setup name="riskWarning">
import { onMounted, ref, defineAsyncComponent } from 'vue'
import { useExpose, useCrud } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

// 工单详情组件
const ComplaintDetail = defineAsyncComponent(() => import('/@/components/ComplaintDetail/index.vue'))
const complaintDetailRef = ref()

// crud组件的ref
const crudRef = ref()
// crud 配置的ref
const crudBinding = ref()
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding })
// 你的crud配置（传入 complaintDetailRef）
const { crudOptions } = createCrudOptions({
  crudExpose,
  context: {},  // 传入空对象作为 context
  complaintDetailRef
})
// 初始化crud配置
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions })

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh()
})
</script>

<style scoped lang="scss">
.risk-warning-container {
  :deep(.fs-crud) {
    .el-card {
      border: none;
      box-shadow: none;
    }
  }
}
</style>
