-- 12345 诉求表
CREATE TABLE IF NOT EXISTS complaints (
    -- 主键：工单编号
    id VARCHAR(50) PRIMARY KEY COMMENT '工单编号',

    -- 基础信息
    complainant_name VARCHAR(100) DEFAULT NULL COMMENT '诉求人姓名',
    complainant_phone VARCHAR(20) DEFAULT NULL COMMENT '诉求人手机号',

    -- 诉求内容
    title VARCHAR(500) DEFAULT NULL COMMENT '诉求标题',
    content TEXT DEFAULT NULL COMMENT '市民诉求',

    -- 分类信息
    category_level1 VARCHAR(100) DEFAULT NULL COMMENT '接诉分类一级',
    category_level2 VARCHAR(100) DEFAULT NULL COMMENT '接诉分类二级',
    category_level3 VARCHAR(100) DEFAULT NULL COMMENT '接诉分类三级',
    category_level4 VARCHAR(100) DEFAULT NULL COMMENT '接诉分类四级',
    order_type VARCHAR(50) DEFAULT NULL COMMENT '工单类型',
    complaint_type VARCHAR(50) DEFAULT NULL COMMENT '诉求类型',
    region VARCHAR(100) DEFAULT NULL COMMENT '所属区域',

    -- 流程信息
    accept_time DATETIME DEFAULT NULL COMMENT '受理时间',
    status VARCHAR(50) DEFAULT NULL COMMENT '工单状态',
    source_channel VARCHAR(50) DEFAULT NULL COMMENT '来源渠道',
    complete_time DATETIME DEFAULT NULL COMMENT '提交办结时间',
    reply_time DATETIME DEFAULT NULL COMMENT '回复时间',
    reply_person TEXT DEFAULT NULL COMMENT '回复诉求人',
    callback_result VARCHAR(200) DEFAULT NULL COMMENT '回访结果',
    handle_department VARCHAR(200) DEFAULT NULL COMMENT '处理部门',

    -- 统计信息
    urge_count INT DEFAULT NULL COMMENT '催单次数',
    supplement_count INT DEFAULT NULL COMMENT '补单次数',
    repeat_count INT DEFAULT NULL COMMENT '重复次数',

    -- 索引
    INDEX idx_accept_time (accept_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='12345诉求表';
