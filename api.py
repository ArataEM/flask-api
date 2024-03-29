import os

import dotenv
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists

dotenv.load_dotenv()

db_user = os.environ.get("DB_USERNAME")
db_pass = os.environ.get("DB_PASSWORD")
db_hostname = os.environ.get("DB_HOSTNAME")
db_name = os.environ.get("DB_NAME")

DB_URI = "mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}".format(
    db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name
)

engine = create_engine(DB_URI, echo=True)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):  # type: ignore
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()


@app.route("/", methods=["GET"])
def hello():
    return "<p>Hello Flask</p>", 200


@app.route("/api/", methods=["GET"])
def api_main():
    return render_template("index.html"), 200


@app.route("/api/students", methods=["GET"])
def get_all_students():
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response = student_list.dump(students)
    return jsonify(response), 200


@app.route("/api/students/get/<int:id>", methods=["GET"])
def get_student(id):
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response = serializer.dump(student_info)
    return jsonify(response), 200


@app.route("/api/students/add", methods=["POST"])
def add_student():
    json_data = request.get_json()
    new_student = Student(
        name=json_data.get("name"),
        email=json_data.get("email"),
        age=json_data.get("age"),
        cellphone=json_data.get("cellphone"),
    )
    new_student.save()

    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201


@app.route("/api/students/modify/<int:id>", methods=["PATCH"])
def patch_student(id):
    json_data = request.get_json()
    student = Student.get_by_id(id)

    if json_data.get("name") is not None:
        student.name = json_data.get("name")
    if json_data.get("email") is not None:
        student.email = json_data.get("email")
    if json_data.get("age") is not None:
        student.age = json_data.get("age")
    if json_data.get("cellphone") is not None:
        student.cellphone = json_data.get("cellphone")

    student.save()

    serializer = StudentSchema()
    data = serializer.dump(student)
    return jsonify(data), 200


@app.route("/api/students/change/<int:id>", methods=["PUT"])
def put_student(id):
    json_data = request.get_json()
    student = Student.get_by_id(id)

    student.name = json_data.get("name")
    student.email = json_data.get("email")
    student.age = json_data.get("age")
    student.cellphone = json_data.get("cellphone")

    student.save()

    serializer = StudentSchema()
    data = serializer.dump(student)
    return jsonify(data), 200


@app.route("/api/students/delete/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = Student.get_by_id(id)
    student.delete()
    return "", 204


@app.route("/api/health-check/ok", methods=["GET"])
def health_check_ok():
    return "OK! Service is Available!", 200


@app.route("/api/health-check/bad", methods=["GET"])
def health_check_bad():
    return "Error", 500


if __name__ == "__main__":
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(debug=True, host="0.0.0.0")
