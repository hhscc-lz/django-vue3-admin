/**
 * 风险预警 CRUD 配置
 */
import { CrudOptions, CrudExpose, CreateCrudOptionsRet, CreateCrudOptionsProps, dict } from '@fast-crud/fast-crud'
import * as api from './api'
import type { RiskTagQuery } from './api'
import { downloadExportFile } from './api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { dictionary } from '/@/utils/dictionary'

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  // 页面请求
  const pageRequest = async (query: RiskTagQuery) => {
    // ✅ 在这里统一处理默认过滤和参数转换
    const requestQuery: any = {
      ...query,
      is_risk: true  // 默认只查询存在风险的数据
    }

    // 处理时间范围筛选参数转换
    if (query.accept_time_range && Array.isArray(query.accept_time_range) && query.accept_time_range.length === 2) {
      requestQuery.accept_time_start = query.accept_time_range[0]
      requestQuery.accept_time_end = query.accept_time_range[1]
      delete requestQuery.accept_time_range
    }

    return await api.GetList(requestQuery)
  }

  // 导出请求
  const exportRequest = async (formData: any) => {
    try {
      // 构建导出查询参数，与列表查询保持一致
      const query: RiskTagQuery = {
        is_risk: true,  // 只导出风险数据
        ...formData
      }

      // 处理时间范围筛选
      if (formData.accept_time_range && formData.accept_time_range.length === 2) {
        query.accept_time_start = formData.accept_time_range[0]
        query.accept_time_end = formData.accept_time_range[1]
        delete query.accept_time_range
      }

      const blob = await api.Export(query)
      downloadExportFile(blob)
      ElMessage.success('导出成功')
    } catch (error) {
      ElMessage.error('导出失败')
      console.error(error)
    }
  }

  return {
    crudOptions: {
      request: {
        pageRequest,
        // ✅ 不再需要 transformQuery 和 transformRes
        // Fast-CRUD 会自动处理标准的分页响应格式
        // 后端返回: { code, msg, page, limit, total, data }
        // Fast-CRUD 期望: { records, currentPage, pageSize, total }
        // 通过 responseMap 配置字段映射
        responseMap: {
          data: 'data',           // 数据列表字段
          currentPage: 'page',    // 当前页字段
          pageSize: 'limit',      // 每页数量字段
          total: 'total'          // 总数字段
        }
      },

      // 操作栏配置
      actionbar: {
        buttons: {
          add: { show: false },  // 隐藏新增按钮
          export: {
            text: '导出',
            type: 'primary',
            click: () => {
              return exportRequest(crudExpose.getSearchFormData())
            }
          }
        }
      },

      // 行操作配置
      rowHandle: {
        fixed: 'right',
        width: 100,
        buttons: {
          view: {
            show: true,
            text: '查看',
            type: 'text'
          },
          edit: { show: false },
          remove: { show: false }
        }
      },

      // 表格配置
      table: {
        size: 'small',
        stripe: true,
        border: true
      },

      // 分页配置
      pagination: {
        pageSize: 20,
        pageSizes: [10, 20, 50, 100]
      },

      // 表单配置 (禁用新增/编辑)
      form: {
        wrapper: {
          is: 'el-dialog',
          width: '900px'
        },
        labelWidth: '120px',
        labelPosition: 'right'
      },

      // 查看表单配置
      viewForm: {
        wrapper: {
          is: 'el-dialog',
          width: '900px',
          top: '5vh'
        },
        labelWidth: '120px',
        labelPosition: 'right',
        group: {
          groups: {
            riskInfo: {
              title: '风险信息',
              columns: ['risk_category', 'risk_reason', 'created_at']
            },
            complaintBasic: {
              title: '工单基础信息',
              columns: ['complaint_id', 'complaint_title', 'complaint_region', 'complaint_status']
            },
            complaintTime: {
              title: '时间信息',
              columns: ['complaint_accept_time', 'complaint_complete_time']
            },
            complaintCategory: {
              title: '分类信息',
              columns: ['complaint_category_level1', 'complaint_category_level2']
            }
          }
        }
      },

      // 字段配置
      columns: {
        // 工单编号
        complaint_id: {
          title: '工单编号',
          type: 'text',
          search: {
            show: true
          },
          column: {
            width: 150,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 风险类别
        risk_category: {
          title: '风险类别',
          type: 'dict-select',
          dict: dict({
            data: dictionary('risk_category')  // ✅ 使用系统字典
          }),
          search: {
            show: true
          },
          column: {
            width: 130,
            sortable: false
          },
          form: {
            show: false
          },
          viewForm: {
            show: true
          }
        },  

        // 诉求标题
        complaint_title: {
          title: '诉求标题',
          type: 'text',
          search: { show: false },
          column: {
            width: 250,
            sortable: false,
            showOverflowTooltip: true
          },
          form: { show: false },
          viewForm: { show: true }
        },
        // 判定原因
        risk_reason: {
          title: '判定原因',
          type: 'textarea',
          search: { show: false },
          column: {
            width: 200,
            sortable: false,
            showOverflowTooltip: true
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 受理时间 (筛选器使用时间范围)
        accept_time_range: {
          title: '受理时间',
          type: 'datetime-range',
          search: {
            show: true,
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

        // 受理时间 (列表显示)
        complaint_accept_time: {
          title: '受理时间',
          type: 'datetime',
          search: { show: false },
          column: {
            width: 160,
            sortable: 'custom',
            formatter: ({ value }: any) => {
              return value ? dayjs(value).format('YYYY-MM-DD HH:mm') : ''
            }
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 工单状态
        complaint_status: {
          title: '工单状态',
          type: 'text',
          search: { show: false },
          column: {
            width: 100,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 办结时间
        complaint_complete_time: {
          title: '办结时间',
          type: 'datetime',
          search: { show: false },
          column: {
            width: 160,
            sortable: false,
            formatter: ({ value }: any) => {
              return value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '-'
            }
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 一级分类
        complaint_category_level1: {
          title: '一级分类',
          type: 'text',
          search: { show: false },
          column: {
            width: 120,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },

        // 二级分类
        complaint_category_level2: {
          title: '二级分类',
          type: 'text',
          search: { show: false },
          column: {
            width: 120,
            sortable: false
          },
          form: { show: false },
          viewForm: { show: true }
        },




      }
    }
  }
}
