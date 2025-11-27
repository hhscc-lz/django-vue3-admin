"""
数据库路由器
将 plugins 下的应用路由到 intelligence 数据库
"""


class IntelligenceDBRouter:
    """
    智能分析数据库路由器
    所有 plugins 下的应用使用 intelligence 数据库
    """

    intelligence_apps = {'risk_warning'}  # plugins 下的应用列表，后续可添加更多

    def db_for_read(self, model, **hints):
        """
        读操作路由
        """
        if model._meta.app_label in self.intelligence_apps:
            return 'intelligence'
        return None

    def db_for_write(self, model, **hints):
        """
        写操作路由
        """
        if model._meta.app_label in self.intelligence_apps:
            return 'intelligence'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        允许关系判断
        """
        # 同数据库内的模型允许关联
        if obj1._meta.app_label in self.intelligence_apps and \
           obj2._meta.app_label in self.intelligence_apps:
            return True
        # 都不在 intelligence_apps 中，允许关联（使用 default 数据库）
        elif obj1._meta.app_label not in self.intelligence_apps and \
             obj2._meta.app_label not in self.intelligence_apps:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        迁移控制
        """
        if app_label in self.intelligence_apps:
            # intelligence 应用只在 intelligence 数据库执行迁移
            return db == 'intelligence'
        # 其他应用只在 default 数据库执行迁移
        return db == 'default'
