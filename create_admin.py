# File: create_admin.py
# Chức năng: Tạo hoặc cập nhật tài khoản admin với mật khẩu đã được băm.
# Chạy file này một lần duy nhất từ terminal: python create_admin.py

from werkzeug.security import generate_password_hash
from database import get_db_connection

# --- Thông tin tài khoản Admin ---
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@thuyloi.edu.vn'
ADMIN_PASSWORD = 'admin123'  # Mật khẩu bạn sẽ dùng để đăng nhập

def create_admin_user():
    """
    Hàm này sẽ kiểm tra sự tồn tại của admin,
    nếu chưa có sẽ tạo mới, nếu có rồi sẽ cập nhật mật khẩu đã băm.
    """
    # 1. Băm mật khẩu
    hashed_password = generate_password_hash(ADMIN_PASSWORD)

    # 2. Lấy kết nối CSDL
    conn = get_db_connection()
    if not conn:
        print("Không thể kết nối đến cơ sở dữ liệu. Vui lòng kiểm tra file database.py")
        return

    try:
        cursor = conn.cursor()

        # 3. Sử dụng câu lệnh MERGE (UPSERT) để chèn hoặc cập nhật admin
        # - Nếu email admin tồn tại, nó sẽ cập nhật mật khẩu và vai trò.
        # - Nếu email chưa tồn tại, nó sẽ chèn một dòng mới.
        merge_sql = """
        MERGE INTO NguoiDung AS Target
        USING (VALUES (?, ?, ?, ?)) AS Source (TenDangNhap, Email, MatKhau, VaiTro)
        ON Target.Email = Source.Email
        WHEN MATCHED THEN
            UPDATE SET
                MatKhau = Source.MatKhau,
                VaiTro = Source.VaiTro,
                TenDangNhap = Source.TenDangNhap
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (TenDangNhap, Email, MatKhau, VaiTro)
            VALUES (Source.TenDangNhap, Source.Email, Source.MatKhau, Source.VaiTro);
        """

        cursor.execute(merge_sql, (ADMIN_USERNAME, ADMIN_EMAIL, hashed_password, 'admin'))
        conn.commit()

        print("="*50)
        print(f"✔️  Tài khoản admin đã được tạo/cập nhật thành công!")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Mật khẩu: {ADMIN_PASSWORD}")
        print("="*50)

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_admin_user()
