import alembic
import alembic.config


def init_db():
    alembic.config.main(argv=["upgrade", "head"])


if __name__ == "__main__":
    init_db()
