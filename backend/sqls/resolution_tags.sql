-- 办结质量标注表
CREATE TABLE IF NOT EXISTS resolution_tags (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 关联工单
    complaint_id VARCHAR(50) NOT NULL COMMENT '工单编号',

    -- 解决情况
    is_resolved VARCHAR(20) DEFAULT NULL COMMENT '是否解决',
    resolved_reason TEXT DEFAULT NULL COMMENT '解决情况判定原因',

    -- 满意度
    is_satisfied VARCHAR(20) DEFAULT NULL COMMENT '是否满意',
    satisfied_reason TEXT DEFAULT NULL COMMENT '满意度判定原因',

    -- 情绪分析
    emotion VARCHAR(50) DEFAULT NULL COMMENT '诉求人情绪',
    emotion_reason TEXT DEFAULT NULL COMMENT '情绪判定原因',

    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_complaint_id (complaint_id),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='办结质量标注表';
