import alembic
import alembic.config


def init_db():
    alembic.config.main(argv=["upgrade", "head"])
