from flask import Blueprint, request, jsonify
from models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# --- Đăng ký tài khoản ---
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Kiểm tra dữ liệu đầu vào
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'msg': 'Thiếu email hoặc mật khẩu'}), 400

    # Kiểm tra email đã tồn tại chưa
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg': 'Email đã tồn tại'}), 400

    # Mã hoá mật khẩu
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # Tạo người dùng mới
    new_user = User(email=data['email'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'Đăng ký thành công'}), 201


# --- Đăng nhập ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'msg': 'Thiếu email hoặc mật khẩu'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'msg': 'Sai email hoặc mật khẩu'}), 401

    # Tạo JWT token
    token = create_access_token(identity=user.id)
    return jsonify({'token': token}), 200
