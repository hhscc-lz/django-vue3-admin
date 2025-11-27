<template>
  <fs-page class="risk-warning-container">
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script lang="ts" setup name="riskWarning">
import { onMounted, ref } from 'vue'
import { useExpose, useCrud } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

// crud组件的ref
const crudRef = ref()
// crud 配置的ref
const crudBinding = ref()
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding })
// 你的crud配置
const { crudOptions } = createCrudOptions({ crudExpose })
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
