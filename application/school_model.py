from .master_database import master_db


class School(master_db.Model):
    __bind_key__ = "master"
    __tablename__ = "schools"

    id = master_db.Column(master_db.Integer, primary_key=True)

    school_name = master_db.Column(master_db.String(200), nullable=False)

    subdomain = master_db.Column(master_db.String(100), unique=True, nullable=False)

    database_name = master_db.Column(master_db.String(100), unique=True, nullable=False)

    status = master_db.Column(master_db.Boolean, default=True)

    created_at = master_db.Column(
        master_db.DateTime,
        server_default=master_db.func.now()
    )