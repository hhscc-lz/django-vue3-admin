-- 风险标注表
CREATE TABLE IF NOT EXISTS risk_tags (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 关联工单
    complaint_id VARCHAR(50) NOT NULL COMMENT '工单编号',

    -- 风险信息
    is_risk BOOLEAN NOT NULL COMMENT '是否风险件（0-否，1-是）',
    risk_category VARCHAR(100) DEFAULT NULL COMMENT '风险类别（模型预测结果，非风险时为NULL）',
    risk_reason TEXT DEFAULT NULL COMMENT '判定原因',

    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_complaint_id (complaint_id),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='风险标注表';
