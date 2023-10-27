class GameRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "playstyle_compass" and model.__name__ == "Game":
            return "games_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "playstyle_compass" and model.__name__ == "Game":
            return "games_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "playstyle_compass" and model_name == "Game":
            return db == "games_db"
        return None
