import pyodbc

# THAY ĐỔI TÊN SERVER CHO PHÙ HỢP VỚI CẤU HÌNH CỦA BẠN
SERVER = 'DESKTOP-N5I5BNI\SQLEXPRESS' # ví dụ: 'DESKTOP-ABC\SQLEXPRESS'
DATABASE = 'CampusSwapDB'

# Chuỗi kết nối sử dụng Windows Authentication
# "Trusted_Connection=yes" cho phép đăng nhập bằng tài khoản Windows hiện tại
connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SERVER};'
    f'DATABASE={DATABASE};'
    f'Trusted_Connection=yes;'
)

def get_db_connection():
    """Tạo và trả về một kết nối đến CSDL."""
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # In ra lỗi chi tiết hơn để dễ dàng gỡ rối
        print(f"Lỗi kết nối CSDL: {ex}")
        return None