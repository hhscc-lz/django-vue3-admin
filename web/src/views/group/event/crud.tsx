/**
 * 群体事件 CRUD 配置
 */
import {
  CreateCrudOptionsRet,
  CreateCrudOptionsProps
} from '@fast-crud/fast-crud'
import * as api from './api'
import type { GroupEventQuery } from './types'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import type { Ref } from 'vue'

export const createCrudOptions = function (
  props: CreateCrudOptionsProps & {
    complaintDetailRef?: Ref<any>
    relatedComplaintsDialogRef?: Ref<any>
  }
): CreateCrudOptionsRet {
  const { crudExpose, complaintDetailRef, relatedComplaintsDialogRef } = props

  // 页面请求
  const pageRequest = async (query: GroupEventQuery) => {
    // 处理时间范围筛选参数转换
    const requestQuery: any = { ...query }

    if (
      query.created_at_range &&
      Array.isArray(query.created_at_range) &&
      query.created_at_range.length === 2
    ) {
      requestQuery.created_at_start = query.created_at_range[0]
      requestQuery.created_at_end = query.created_at_range[1]
      delete requestQuery.created_at_range
    }

    return await api.GetList(requestQuery)
  }

  return {
    crudOptions: {
      request: {
        pageRequest,
        // 响应字段映射
        responseMap: {
          data: 'data',
          currentPage: 'page',
          pageSize: 'limit',
          total: 'total'
        }
      },

      // 操作栏配置
      actionbar: {
        buttons: {
          add: { show: false } // 隐藏新增按钮（只读）
        }
      },

      // 行操作配置
      rowHandle: {
        fixed: 'right',
        width: 220,
        buttons: {
          // 查看触发工单详情
          view: {
            show: true,
            text: '查看详情',
            type: 'primary',
            link: true,
            click: ({ row }: any) => {
              // 打开触发工单详情
              if (complaintDetailRef && complaintDetailRef.value) {
                complaintDetailRef.value.open(row.trigger_complaint_id)
              } else {
                ElMessage.warning('工单详情组件未加载')
              }
            }
          },
          // 自定义按钮：查看关联工单
          viewComplaints: {
            show: true,
            text: '关联工单',
            type: 'success',
            link: true,
            order: 2,
            click: ({ row }: any) => {
              console.log('点击关联工单按钮，row:', row)
              // 打开关联工单对话框
              if (relatedComplaintsDialogRef && relatedComplaintsDialogRef.value) {
                relatedComplaintsDialogRef.value.open(row.id, row.title)
              } else {
                ElMessage.warning('关联工单组件未加载')
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
          width: '900px',
          top: '5vh'
        },
        labelWidth: '150px',
        labelPosition: 'right',
        group: {
          groups: {
            basic: {
              title: '基本信息',
              columns: ['title', 'region', 'complaint_count', 'created_at']
            },
            trigger: {
              title: '触发工单',
              columns: ['trigger_complaint_id', 'trigger_complaint_title']
            }
          }
        }
      },

      // 字段配置
      columns: {
        // ID
        id: {
          title: 'ID',
          type: 'number',
          column: {
            width: 80,
            sortable: false
          },
          form: { show: false }
        },

        // 事件标题
        title: {
          title: '事件标题',
          type: 'text',
          search: {
            show: true
          },
          column: {
            width: 300,
            sortable: false,
            showOverflowTooltip: true
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 区域
        region: {
          title: '主要区域',
          type: 'text',
          search: {
            show: true
          },
          column: {
            width: 120,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 关联工单数量
        complaint_count: {
          title: '关联工单数',
          type: 'number',
          search: { show: false },
          column: {
            width: 120,
            sortable: 'custom',
            align: 'center'
          },
          form: { show: false },
          viewForm: {
            show: true,
            component: {
              name: 'el-tag',
              type: 'warning',
              size: 'large'
            }
          }
        },

        // 创建时间范围（筛选器）
        created_at_range: {
          title: '创建时间',
          type: 'datetime-range',
          search: {
            show: true,
            col: { span: 8 },
            component: {
              name: 'el-date-picker',
              type: 'datetimerange',
              startPlaceholder: '开始时间',
              endPlaceholder: '结束时间',
              valueFormat: 'YYYY-MM-DD HH:mm:ss'
            }
          },
          column: { show: false },
          form: { show: false }
        },

        // 创建时间（列表显示）
        created_at: {
          title: '创建时间',
          type: 'datetime',
          search: { show: false },
          column: {
            width: 180,
            sortable: 'custom',
            formatter: ({ value }: any) => {
              return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : ''
            }
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 触发工单ID
        trigger_complaint_id: {
          title: '触发工单ID',
          type: 'text',
          search: { show: false },
          column: {
            width: 150,
            sortable: false
          },
          form: { show: false },
          viewForm: {
            show: true,
            component: {
              name: 'el-link',
              type: 'primary',
              underline: false,
              onClick: ({ value }: any) => {
                // 点击查看触发工单详情
                if (complaintDetailRef && complaintDetailRef.value) {
                  complaintDetailRef.value.open(value)
                }
              }
            }
          }
        },

        // 触发工单标题
        trigger_complaint_title: {
          title: '触发工单标题',
          type: 'text',
          search: { show: false },
          column: {
            width: 250,
            sortable: false,
            showOverflowTooltip: true
          },
          form: { show: false },
          viewForm: { show: true }
        }
      }
    }
  }
}
