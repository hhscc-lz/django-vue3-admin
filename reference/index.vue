<template>
	<div class="risk-warning-container">
		<el-row :gutter="20" style="height: 100%;">
			<!-- 左侧诉求列表 -->
			<el-col :span="10">
				<el-card class="left-panel">
					<template #header>
						<div class="card-header">
							<span>未评估风险件列表</span>
						</div>
					</template>

					<div class="complaint-list">
						<div v-if="isLoadingComplaints" class="loading-list">
							<el-loading-spinner />
							<p>正在加载投诉数据...</p>
						</div>
						<div v-else-if="error" class="error-list">
							<el-result
								icon="error"
								title="数据加载失败"
								:sub-title="error"
							>
								<template #extra>
									<el-button type="primary" @click="loadLatestComplaints">重试</el-button>
								</template>
							</el-result>
						</div>
						<div v-else-if="filteredComplaints.length === 0" class="empty-list">
							<el-empty
								description="暂无未评估的诉求件"
								:image-size="80"
							/>
						</div>
						<div v-else>
							<div
								v-for="item in filteredComplaints"
								:key="item.serial_number"
								class="complaint-item"
								:class="{ active: selectedComplaint?.serial_number === item.serial_number }"
								@click="selectComplaint(item)"
							>
								<div class="complaint-header">
									<div class="complaint-no">{{ item.serial_number }}</div>
									<div class="complaint-title">{{ item.title }}</div>
								</div>
								<div class="complaint-content">{{ item.content }}</div>
								<div class="complaint-meta">
									<span class="time">{{ item.time }}</span>
									<span class="status">{{ item.status }}</span>
									<span class="area">{{ item.handling_area }}</span>
								</div>
							</div>
						</div>
					</div>

					<el-pagination
						v-model:current-page="currentPage"
						v-model:page-size="pageSize"
						:total="totalComplaints"
						layout="prev, pager, next"
						@current-change="handlePageChange"
						style="margin-top: 16px; text-align: center;"
					/>
				</el-card>
			</el-col>

			<!-- 右侧风险评估结果 -->
			<el-col :span="14">
				<el-card class="right-panel">
					<template #header>
						<span>风险评估结果</span>
					</template>

					<div v-if="!selectedComplaint" class="no-selection">
						<el-empty description="请从左侧选择一个诉求件进行风险评估" />
					</div>

					<div v-else class="assessment-content">
						<!-- 加载状态 -->
						<div v-if="isLoading" class="loading-content">
							<el-card class="loading-card" shadow="never">
								<div class="loading-wrapper">
									<el-icon class="is-loading"><Loading /></el-icon>
									<span>正在进行风险评估...</span>
								</div>
							</el-card>
						</div>

						<!-- 风险评估结果面板 -->
						<template v-else>
							<el-card v-if="riskInfo.risk_type" class="risk-result-card" shadow="never">
								<template #header>
									<span>风险评估结果</span>
								</template>

								<div class="risk-overview">
									<el-descriptions :column="2" border>
										<el-descriptions-item label="风险类型">
											<el-tag :type="getRiskTypeColor(riskInfo.risk_type)" size="large">
												{{ riskInfo.risk_type }}
											</el-tag>
										</el-descriptions-item>
										<el-descriptions-item label="风险等级">
											<el-tag :type="getRiskLevelColor(riskInfo.risk_level)" size="large">
												{{ riskInfo.risk_level }}
											</el-tag>
										</el-descriptions-item>
										<el-descriptions-item label="风险评分" :span="2">
											<div class="risk-score">
												<el-progress
													:percentage="(riskInfo.risk_score / 10) * 100"
													:color="getRiskScoreColor(riskInfo.risk_score)"
													:stroke-width="20"
													text-inside
												/>
												<span class="score-text">{{ riskInfo.risk_score }}/10</span>
											</div>
										</el-descriptions-item>
									</el-descriptions>
								</div>

								<el-divider />

								<div class="risk-details">
									<h4>风险分析依据</h4>
									<el-card class="reason-card" shadow="never">
										<p class="risk-reason">{{ riskInfo.risk_reason }}</p>
									</el-card>
								</div>

								<el-divider />

								<!-- 风险处置建议 -->
								<div class="risk-suggestions">
									<h4>处置建议</h4>
									<el-alert
										:title="getSuggestionTitle(riskInfo.risk_level)"
										:type="getSuggestionType(riskInfo.risk_level)"
										:description="getSuggestionContent(riskInfo.risk_level, riskInfo.risk_type)"
										show-icon
										:closable="false"
									/>
								</div>
							</el-card>

							<!-- 无风险信息提示 -->
							<el-card v-if="!riskInfo.risk_type && !isLoading" class="no-risk-card" shadow="never">
								<el-empty description="未识别到有效的风险信息" :image-size="60" />
							</el-card>
						</template>
					</div>
				</el-card>
			</el-col>
		</el-row>
	</div>
</template>

<script setup lang="ts" name="riskWarningAnnotation">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useDatasetApi } from '/@/api/dataset'
import type { ComplaintItem, LatestComplaintsResponse, RiskAssessmentResponse } from '/@/types/dataset'

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(10)
const selectedComplaint = ref<ComplaintItem | null>(null)
const riskAnnotation = ref<RiskAssessmentResponse | null>(null)
const isLoading = ref(false)
const isLoadingComplaints = ref(false)
const complaints = ref<ComplaintItem[]>([])
const error = ref<string | null>(null)

// 计算属性
const filteredComplaints = computed(() => {
	// 分页处理
	const start = (currentPage.value - 1) * pageSize.value
	const end = start + pageSize.value
	return complaints.value.slice(start, end)
})

const totalComplaints = computed(() => complaints.value.length)

// 获取当前选中投诉的风险评估信息
const riskInfo = computed(() => {
	if (!riskAnnotation.value || !riskAnnotation.value.data || !riskAnnotation.value.data.risk) {
		return {}
	}

	const risk = riskAnnotation.value.data.risk
	return {
		risk_type: risk.type,
		risk_level: risk.level,
		risk_score: risk.score,
		risk_reason: risk.reason
	}
})

// 样式和文本映射方法
const getRiskTypeColor = (type: string) => {
	const colorMap: Record<string, string> = {
		'群体性事件风险': 'danger',
		'信访风险': 'warning',
		'舆情风险': 'primary',
		'安全风险': 'danger',
		'经济风险': 'warning',
		'社会稳定风险': 'danger'
	}
	return colorMap[type] || 'info'
}

const getRiskLevelColor = (level: string) => {
	const colorMap: Record<string, string> = {
		'高风险': 'danger',
		'中风险': 'warning',
		'低风险': 'success',
		'无风险': 'info'
	}
	return colorMap[level] || 'info'
}

const getRiskScoreColor = (score: number) => {
	if (score >= 7) return '#F56C6C'
	if (score >= 4) return '#E6A23C'
	return '#67C23A'
}

const getSuggestionTitle = (level: string) => {
	const titleMap: Record<string, string> = {
		'高风险': '紧急处置建议',
		'中风险': '重点关注建议',
		'低风险': '常规处理建议',
		'无风险': '正常处理建议'
	}
	return titleMap[level] || '处理建议'
}

const getSuggestionType = (level: string) => {
	const typeMap: Record<string, 'success' | 'warning' | 'error' | 'info'> = {
		'高风险': 'error',
		'中风险': 'warning',
		'低风险': 'success',
		'无风险': 'info'
	}
	return typeMap[level] || 'info'
}

const getSuggestionContent = (level: string, type: string) => {
	if (level === '高风险') {
		return `该诉求存在${type}，建议立即启动应急预案，派专人处理，24小时内响应，必要时上报上级部门协调处置。`
	} else if (level === '中风险') {
		return `该诉求存在一定${type}，建议优先处理，48小时内响应，密切关注事态发展，做好预防措施。`
	} else if (level === '低风险') {
		return `该诉求风险较低，按正常流程处理即可，7个工作日内响应，注意回访满意度。`
	} else {
		return `该诉求未发现明显风险因素，按常规程序处理，关注服务质量。`
	}
}

// 初始化API
const datasetApi = useDatasetApi()

// API调用函数
const assessRiskInfo = async (content: string) => {
	try {
		isLoading.value = true

		const result = await datasetApi.assessRisk(content)

		if (result.code === 2000 && result.data) {
			riskAnnotation.value = result
			ElMessage.success('风险评估完成')
		} else {
			throw new Error(result.msg || '风险评估失败')
		}
	} catch (error: any) {
		console.error('风险评估错误:', error)
		ElMessage.error(`风险评估失败: ${error.message || error.msg || '未知错误'}`)
		riskAnnotation.value = null
	} finally {
		isLoading.value = false
	}
}

// 加载最新投诉数据
const loadLatestComplaints = async () => {
	try {
		isLoadingComplaints.value = true
		error.value = null

		const result = await datasetApi.getLatestComplaints()

		if (result.code === 2000 && result.data) {
			complaints.value = result.data
			ElMessage.success('投诉数据加载成功')
		} else {
			throw new Error(result.msg || '数据加载失败')
		}
	} catch (err: any) {
		// 检查是否是API成功响应但数据验证失败
		if (err?.code === 2000 && err?.data) {
			complaints.value = err.data
			ElMessage.success('投诉数据加载成功')
		} else {
			console.error('加载投诉数据错误:', err)
			error.value = err.msg || err.message || '网络请求失败'
			ElMessage.error(`数据加载失败: ${error.value}`)
		}
	} finally {
		isLoadingComplaints.value = false
	}
}

// 方法
const handlePageChange = (page: number) => {
	currentPage.value = page
	// 切换页面时清空选择
	selectedComplaint.value = null
	riskAnnotation.value = null
}

const selectComplaint = (complaint: ComplaintItem) => {
	selectedComplaint.value = complaint
	// 选中诉求后，自动调用API进行风险评估
	if (complaint?.content) {
		assessRiskInfo(complaint.content)
	} else {
		riskAnnotation.value = null
	}
}

onMounted(async () => {
	// 页面加载时先加载真实数据
	await loadLatestComplaints()
})
</script>

<style scoped lang="scss">
.risk-warning-container {
	padding: 20px;
	height: calc(100vh - 120px);

	.left-panel, .right-panel {
		height: 100%;

		.el-card__body {
			padding: 16px;
			height: calc(100% - 57px);
			overflow: hidden;
		}
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.complaint-list {
		height: calc(100% - 60px);
		overflow-y: auto;

		.empty-list, .error-list, .loading-list {
			height: 100%;
			display: flex;
			align-items: center;
			justify-content: center;
			flex-direction: column;
		}

		.complaint-item {
			padding: 12px;
			border: 1px solid var(--el-border-color-lighter);
			border-radius: 6px;
			margin-bottom: 8px;
			cursor: pointer;
			transition: all 0.3s;

			&:hover {
				border-color: var(--el-color-primary);
				background-color: var(--el-color-primary-light-9);
			}

			&.active {
				border-color: var(--el-color-primary);
				background-color: var(--el-color-primary-light-8);
				box-shadow: 0 2px 4px var(--el-color-primary-light-5);
			}

			.complaint-header {
				margin-bottom: 6px;

				.complaint-no {
					font-size: 11px;
					color: var(--el-color-primary);
					font-weight: 500;
					margin-bottom: 4px;
				}

				.complaint-title {
					font-weight: 600;
					color: var(--el-text-color-primary);
					font-size: 14px;
				}
			}

			.complaint-content {
				color: var(--el-text-color-regular);
				font-size: 12px;
				line-height: 1.4;
				margin-bottom: 8px;
				overflow: hidden;
				text-overflow: ellipsis;
				display: -webkit-box;
				-webkit-line-clamp: 2;
				-webkit-box-orient: vertical;
			}

			.complaint-meta {
				display: flex;
				justify-content: space-between;
				font-size: 11px;
				color: var(--el-text-color-placeholder);

				.time {
					color: var(--el-color-info);
				}

				.area {
					color: var(--el-color-success);
				}
			}
		}
	}

	.assessment-content {
		height: 100%;
		overflow-y: auto;

		.loading-card {
			.loading-wrapper {
				text-align: center;
				padding: 40px 20px;

				.el-icon {
					font-size: 32px;
					color: var(--el-color-primary);
					margin-bottom: 12px;
				}

				span {
					display: block;
					color: var(--el-text-color-regular);
					font-size: 14px;
				}
			}
		}

		.risk-result-card {
			margin-bottom: 16px;

			.risk-overview {
				margin-bottom: 16px;

				.risk-score {
					display: flex;
					align-items: center;
					gap: 12px;

					.el-progress {
						flex: 1;
					}

					.score-text {
						font-weight: 600;
						font-size: 16px;
						color: var(--el-text-color-primary);
						min-width: 50px;
					}
				}
			}

			.risk-details {
				h4 {
					margin: 0 0 12px 0;
					color: var(--el-text-color-primary);
					font-size: 16px;
				}

				.reason-card {
					background-color: var(--el-fill-color-extra-light);

					.risk-reason {
						margin: 0;
						line-height: 1.6;
						color: var(--el-text-color-regular);
					}
				}
			}

			.risk-suggestions {
				h4 {
					margin: 0 0 12px 0;
					color: var(--el-text-color-primary);
					font-size: 16px;
				}
			}
		}

		.no-risk-card {
			display: flex;
			align-items: center;
			justify-content: center;
			min-height: 300px;
		}
	}

	.no-selection {
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}
}
</style>