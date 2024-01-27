"""This module contains the database routers."""


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
        if (
            obj1._meta.app_label == "playstyle_compass"
            and obj2._meta.app_label == "playstyle_compass"
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "playstyle_compass" and model_name == "Game":
            return db == "games_db"
        return None


class ReviewRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "playstyle_compass" and model.__name__ == "Review":
            return "games_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "playstyle_compass" and model.__name__ == "Review":
            return "games_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == "playstyle_compass"
            and obj1.__class__.__name__ == "Review"
            and obj2._meta.app_label == "auth"
            and obj2.__class__.__name__ == "User"
        ):
            return True
        if (
            obj2._meta.app_label == "playstyle_compass"
            and obj2.__class__.__name__ == "Review"
            and obj1._meta.app_label == "auth"
            and obj1.__class__.__name__ == "User"
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "playstyle_compass" and model_name == "Review":
            return db == "games_db"
        return None


class FranchiseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "playstyle_compass" and model.__name__ == "Franchise":
            return "games_db"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "playstyle_compass" and model.__name__ == "Franchise":
            return "games_db"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == "playstyle_compass"
            and obj2._meta.app_label == "playstyle_compass"
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "playstyle_compass" and model_name == "Franchise":
            return db == "games_db"
        return None