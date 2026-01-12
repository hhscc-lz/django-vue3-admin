<template>
  <fs-page class="daily-summary-container">
    <fs-crud ref="crudRef" v-bind="crudBinding" />

    <!-- 重新生成对话框 -->
    <RegenerateDialog ref="regenerateDialogRef" />
  </fs-page>
</template>

<script lang="ts" setup name="dailySummary">
import { onMounted, ref, defineAsyncComponent } from 'vue'
import { useExpose, useCrud } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

// 重新生成对话框组件
const RegenerateDialog = defineAsyncComponent(
  () => import('./RegenerateDialog.vue')
)

const regenerateDialogRef = ref()

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
  regenerateDialogRef
})

// 初始化crud配置
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions })

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh()
})
</script>

<style scoped lang="scss">
.daily-summary-container {
  :deep(.fs-crud) {
    .el-card {
      border: none;
      box-shadow: none;
    }
  }
}
</style>
