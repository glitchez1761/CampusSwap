from flask import Flask
from models import db, bcrypt
from auth import auth_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_swap.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api')
@app.route('/')
def index():
    return "<h1>Chào mừng bạn đến với CampusSwap API!</h1>"

if __name__ == '__main__':
    from waitress import serve
    with app.app_context():
        db.create_all()
    serve(app, host="0.0.0.0", port=8080)