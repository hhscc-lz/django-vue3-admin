/**
 * 群体事件每日摘要 CRUD 配置
 */
import { CreateCrudOptionsRet, CreateCrudOptionsProps } from '@fast-crud/fast-crud'
import * as api from './api'
import type { DailySummaryQuery } from './types'
import dayjs from 'dayjs'
import type { Ref } from 'vue'

export const createCrudOptions = function (
  props: CreateCrudOptionsProps & {
    regenerateDialogRef?: Ref<any>
  }
): CreateCrudOptionsRet {
  const { crudExpose, regenerateDialogRef } = props

  // 页面请求 - 直接返回原始响应，由全局 transformRes 处理
  const pageRequest = async (query: DailySummaryQuery) => {
    return await api.GetList(query)
  }

  return {
    crudOptions: {
      request: {
        pageRequest
      },

      // 操作栏配置
      actionbar: {
        buttons: {
          add: { show: false }
        }
      },

      // 行操作配置
      rowHandle: {
        fixed: 'right',
        width: 180,
        buttons: {
          view: {
            show: true,
            text: '查看',
            type: 'primary',
            link: true
          },
          regenerate: {
            show: true,
            text: '重新生成',
            type: 'warning',
            link: true,
            order: 2,
            click: ({ row }: any) => {
              if (regenerateDialogRef && regenerateDialogRef.value) {
                regenerateDialogRef.value.open(row.summary_date)
              }
            }
          },
          edit: { show: false },
          remove: { show: false }
        }
      },

      // 表格配置
      table: {
        size: 'default',
        stripe: true,
        border: true
      },

      // 分页配置
      pagination: {
        pageSize: 20,
        pageSizes: [10, 20, 50, 100]
      },

      // 查看表单配置
      viewForm: {
        wrapper: {
          is: 'el-dialog',
          width: '800px',
          top: '5vh'
        },
        labelWidth: '100px',
        labelPosition: 'right'
      },

      // 字段配置
      columns: {
        id: {
          title: 'ID',
          type: 'number',
          column: {
            width: 80,
            sortable: false
          },
          form: { show: false }
        },

        summary_date: {
          title: '摘要日期',
          type: 'text',
          search: {
            show: true,
            component: {
              name: 'el-date-picker',
              type: 'date',
              valueFormat: 'YYYY-MM-DD',
              placeholder: '选择日期'
            }
          },
          column: {
            width: 120,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },

        title: {
          title: '日报标题',
          type: 'text',
          search: { show: false },
          column: {
            width: 200,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },

        content: {
          title: '日报内容',
          type: 'textarea',
          search: { show: false },
          column: {
            width: 400,
            showOverflowTooltip: true
          },
          form: { show: false },
          viewForm: {
            show: true,
            component: {
              style: 'white-space: pre-wrap; line-height: 1.8;'
            }
          }
        },

        event_count: {
          title: '事件数量',
          type: 'number',
          search: { show: false },
          column: {
            width: 100,
            align: 'center'
          },
          form: { show: false },
          viewForm: { show: true }
        },

        created_at: {
          title: '创建时间',
          type: 'datetime',
          search: { show: false },
          column: {
            width: 180,
            formatter: ({ value }: any) => {
              return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : ''
            }
          },
          form: { show: false },
          viewForm: { show: true }
        }
      }
    }
  }
}
