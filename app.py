from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
import io
import csv

app = Flask(__name__)
# Cần có SECRET_KEY để sử dụng session
app.config['SECRET_KEY'] = 'your_very_secret_key_here'

@app.route('/')
def home():
    # Chuyển hướng đến trang đăng nhập nếu chưa đăng nhập
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Nếu là admin, chuyển đến trang quản trị
    if session.get('vai_tro') == 'admin':
        return redirect(url_for('admin_dashboard'))

    # Đối với người dùng thông thường, hiển thị trang chào mừng với nút đăng xuất
    # Đoạn HTML này được trả về trực tiếp mà không cần file template riêng
    ten_dang_nhap = session.get('ten_dang_nhap', 'Khách')
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>Trang chính - CampusSwap</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    </head>
    <body class="container mt-5">
        <h1>Chào mừng bạn, {ten_dang_nhap}!</h1>
        <p>Bạn đã đăng nhập thành công vào CampusSwap.</p>
        <a href="{url_for('logout')}" class="btn btn-danger">Đăng xuất</a>
    </body>
    </html>
    """
# --- CHỨC NĂNG ĐĂNG KÝ ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ten_dang_nhap = request.form['ten_dang_nhap']
        email = request.form['email']
        mat_khau = request.form['mat_khau']

        # Băm mật khẩu để bảo mật
        hashed_password = generate_password_hash(mat_khau)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Kiểm tra xem email hoặc tên đăng nhập đã tồn tại chưa
            cursor.execute("SELECT * FROM NguoiDung WHERE Email = ? OR TenDangNhap = ?", (email, ten_dang_nhap))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Email hoặc Tên đăng nhập đã tồn tại!', 'danger')
                return redirect(url_for('register'))

            # Thêm người dùng mới vào CSDL
            cursor.execute(
                "INSERT INTO NguoiDung (TenDangNhap, Email, MatKhau) VALUES (?, ?, ?)",
                (ten_dang_nhap, email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# --- CHỨC NĂNG ĐĂNG NHẬP ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        mat_khau = request.form['mat_khau']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM NguoiDung WHERE Email = ?", (email,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user.MatKhau, mat_khau):
                # Lưu thông tin người dùng vào session
                session['user_id'] = user.ID
                session['ten_dang_nhap'] = user.TenDangNhap
                session['vai_tro'] = user.VaiTro
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Email hoặc mật khẩu không đúng.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('login'))

# --- TRANG QUẢN TRỊ VÀ XUẤT BÁO CÁO ---
@app.route('/admin/dashboard')
def admin_dashboard():
    # Bảo vệ trang: chỉ admin mới được vào
    if 'user_id' not in session or session.get('vai_tro') != 'admin':
        flash('Bạn không có quyền truy cập trang này!', 'danger')
        return redirect(url_for('login'))

    return render_template('admin_dashboard.html')

@app.route('/admin/export_report')
def export_report():
    # Bảo vệ chức năng: chỉ admin mới được xuất báo cáo
    if 'user_id' not in session or session.get('vai_tro') != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # Truy vấn dữ liệu cần xuất (ví dụ: tất cả bài đăng)
        query = """
            SELECT b.ID, b.TieuDe, b.NoiDung, b.NgayDang, b.TrangThai, n.TenDangNhap
            FROM BaiDang b
            JOIN NguoiDung n ON b.IDNguoiDung = n.ID
        """
        cursor.execute(query)
        data = cursor.fetchall()
        conn.close()

        # Tạo file CSV trong bộ nhớ
        output = io.StringIO()
        writer = csv.writer(output)

        # Ghi header
        writer.writerow(['ID Bài Đăng', 'Tiêu đề', 'Nội dung', 'Ngày Đăng', 'Trạng thái', 'Người Đăng'])
        # Ghi dữ liệu
        for row in data:
            writer.writerow(row)

        output.seek(0)

        # Trả về file cho người dùng tải xuống
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=bao_cao_bai_dang.csv"}
        )

if __name__ == '__main__':
    app.run(debug=True)