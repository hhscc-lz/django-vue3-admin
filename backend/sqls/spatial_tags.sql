-- 空间标注表
CREATE TABLE IF NOT EXISTS spatial_tags (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 关联工单
    complaint_id VARCHAR(50) NOT NULL COMMENT '工单编号',

    -- 地址信息
    address VARCHAR(500) DEFAULT NULL COMMENT '提取的诉求地址',
    address_type VARCHAR(50) DEFAULT NULL COMMENT '地址类型',

    -- 坐标信息
    longitude DECIMAL(10, 7) DEFAULT NULL COMMENT '经度',
    latitude DECIMAL(10, 7) DEFAULT NULL COMMENT '纬度',

    -- 定位信息
    district VARCHAR(100) DEFAULT NULL COMMENT '区县',
    street VARCHAR(100) DEFAULT NULL COMMENT '街道',
    community VARCHAR(200) DEFAULT NULL COMMENT '小区',

    -- 时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_complaint_id (complaint_id),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='空间标注表';
