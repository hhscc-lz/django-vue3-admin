-- 主体标注表
CREATE TABLE IF NOT EXISTS subject_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id VARCHAR(50) NOT NULL COMMENT '工单编号',

    -- 主体基本信息
    subject_name VARCHAR(200) DEFAULT NULL COMMENT '被投诉主体名称',
    subject_type VARCHAR(50) DEFAULT NULL COMMENT '主体类型（商业机构/公共服务机构/无）',

    -- 商业机构详细信息（仅商业机构时填充）
    industry VARCHAR(50) DEFAULT NULL COMMENT '行业类型',
    scale VARCHAR(50) DEFAULT NULL COMMENT '企业规模',
    complaint_nature VARCHAR(50) DEFAULT NULL COMMENT '投诉性质',
    model VARCHAR(50) DEFAULT NULL COMMENT '经营形式',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_complaint_id (complaint_id),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='主体标注表';
