import importlib
import os
import pkgutil

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine

from mdp2mailservice.core.config import settings

admin_panel: Admin | None = None


def create_admin_panel(app: FastAPI, db_engine: AsyncEngine) -> Admin:
    global admin_panel
    admin_panel = Admin(app, db_engine, title="mdp2mailservice", base_url="/admin")

    for _, pkg, is_pkg in pkgutil.iter_modules([os.path.normpath(os.path.dirname(__file__) + "/../")]):
        try:
            if is_pkg:
                importlib.import_module(f"{settings.APP_NAME}.{pkg}.admin")
        except ModuleNotFoundError:
            pass

    for view in ModelView.__subclasses__():
        admin_panel.add_view(view)

    return admin_panel
