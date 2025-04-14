from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # 모든 도메인의 요청 허용

# MariaDB 연결 설정
DB_CONFIG = {
    'host': '192.168.226.131',  # DB 서버 IP
    'user': 'webuser',          # DB 사용자
    'password': '1234',         # DB 비밀번호
    'db': 'testdb',             # 데이터베이스 이름
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

@app.route('/login', methods=['POST'])
def login():
    """사용자 로그인 API 엔드포인트"""
    # JSON 형식의 요청 데이터 가져오기
    data = request.get_json()
    
    # 요청 데이터 검증
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '아이디와 비밀번호를 모두 입력해주세요.'}), 400
    
    username = data['username']
    password = data['password']
    
    # 데이터베이스 연결
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '데이터베이스 연결에 실패했습니다.'}), 500
    
    try:
        with connection.cursor() as cursor:
            # users 테이블에서 사용자 조회 (id, passwd 필드만 있는 테이블)
            sql = "SELECT * FROM users WHERE id = %s AND passwd = %s"
            cursor.execute(sql, (username, password))
            user = cursor.fetchone()
            
            if user:
                # 사용자 찾음 - 로그인 성공
                return jsonify({'success': True, 'message': '로그인 성공'}), 200
            else:
                # 사용자를 찾을 수 없음 - 로그인 실패
                return jsonify({'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401
    except Exception as e:
        # 데이터베이스 쿼리 오류
        print(f"데이터베이스 쿼리 오류: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500
    finally:
        # 연결 닫기
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
