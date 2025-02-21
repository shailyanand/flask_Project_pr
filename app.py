from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


@app.route("/homepage")
def homepage():
    return "Welcome to the homepage!"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        # validate email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({"message": "Invalid email"}), 400
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        # print(existing_user)
        if existing_user:
            return jsonify({"message": "User with this username or email already exists"}), 400
        # Here you can add code to save the user to a database
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": f"User {username} created successfully!"}), 201
    return render_template("signup.html")

@app.route("/allusers", methods=["GET"])
def allusers():
    users = User.query.all()
    return jsonify([{"username": user.username, "email": user.email} for user in users])



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)