class MyDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'watchapp':
            return 'secondary'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'watchapp':
            return 'secondary'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'watchapp' or obj2._meta.app_label == 'watchapp':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
            # Allow migrations for all other models in 'watchapp' on the second database
        if app_label == 'watchapp':
            return db == 'sqlite'
        # Prevent migrations for 'my_app' models on other databases
        elif db == 'default':
            return False
        return None