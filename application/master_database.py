from flask_sqlalchemy import SQLAlchemy

master_db = SQLAlchemy()


def init_master_db(app):
    app.config["SQLALCHEMY_BINDS"] = {
        "master": "postgresql://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/erp_master"
    }

    master_db.init_app(app)