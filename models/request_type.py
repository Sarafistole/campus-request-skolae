from extensions import db

class RequestType(db.Model):
    __tablename__ = "request_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)