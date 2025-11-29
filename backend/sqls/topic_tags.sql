-- 专题标注表
CREATE TABLE IF NOT EXISTS topic_tags (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 关联工单
    complaint_id VARCHAR(50) NOT NULL COMMENT '工单编号',

    -- 专题信息
    topic_name VARCHAR(50) NOT NULL COMMENT '专题名称',
    topic_fields JSON DEFAULT NULL COMMENT '专题细分字段（JSON格式）',

    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_complaint_id (complaint_id),
    INDEX idx_topic_name (topic_name),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专题标注表';
