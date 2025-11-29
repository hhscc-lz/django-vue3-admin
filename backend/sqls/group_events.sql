-- 群体事件主表
CREATE TABLE IF NOT EXISTS group_events (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 事件信息
    title VARCHAR(500) NOT NULL COMMENT '大模型生成的摘要标题',
    trigger_complaint_id VARCHAR(50) NOT NULL COMMENT '触发识别的诉求ID',
    complaint_count INT NOT NULL COMMENT '关联诉求数量',

    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_trigger_complaint (trigger_complaint_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='群体事件主表';


-- 诉求关联表
CREATE TABLE IF NOT EXISTS group_event_complaints (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 关联信息
    group_event_id INT NOT NULL COMMENT '群体事件ID',
    complaint_id VARCHAR(50) NOT NULL COMMENT '诉求ID',

    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_group_event_id (group_event_id),
    INDEX idx_complaint_id (complaint_id),
    FOREIGN KEY (group_event_id) REFERENCES group_events(id) ON DELETE CASCADE,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='群体事件诉求关联表';
