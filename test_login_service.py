import unittest
import os
import time
from login_service import app, db
from models import User
from werkzeug.security import generate_password_hash
from faker import Faker
from sqlalchemy.exc import OperationalError

class LoginServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

        app.config['TESTING'] = True
        # 기존 DB 사용
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'mysql')}@{os.getenv('DB_HOST', 'mysql')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'user_db')}"
        self.client = app.test_client()

        # Wait for MySQL to be available
        self._wait_for_mysql()

        # 직접 테스트용 데이터 추가
        with app.app_context():
            fake_student_id = self.fake.random_number(digits=8)
            fake_department = self.fake.word()
            fake_name = self.fake.name()
            fake_email = self.fake.email()
            fake_phone_number = '010-1234-1234'  # 예시 번호
            fake_password = 'password'

            # 테스트용 사용자 추가
            test_user = User(
                student_id=str(fake_student_id),
                department=fake_department,
                name=fake_name,
                email=fake_email,
                phone_number=fake_phone_number,
                password_hash=generate_password_hash(fake_password)  # 비밀번호 해시 생성
            )
            db.session.add(test_user)
            db.session.commit()

    def _wait_for_mysql(self):
        """Ensure MySQL is available before tests run."""
        retries = 30
        while retries > 0:
            try:
                with app.app_context():  # Push the app context before trying the connection
                    db.engine.connect()
                return
            except OperationalError:
                retries -= 1
                time.sleep(2)
        raise Exception("MySQL not available after retries")

    def tearDown(self):
        """Clean up after each test (optional, as we're not deleting tables)."""
        with app.app_context():
            db.session.remove()
            # No db.drop_all() to preserve existing data

    def test_login(self):
        """Test the login route."""
        with app.app_context():  # Ensure the app context is pushed
            # Get the test user from the database (방금 추가한 사용자)
            test_user = User.query.order_by(User.user_id.desc()).first()

        # 로그인 테스트 시, 실제로 제공된 비밀번호를 확인해야 합니다.
        password = 'password'  # 암호화된 비밀번호와 일치하는 비밀번호
        response = self.client.post('/login', data=dict(
            username=test_user.name,
            password=password
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

    def test_register(self):
        """Test the register route."""
        response = self.client.post('/register', data=dict(
            student_id=str(self.fake.random_number(digits=8)),
            department=self.fake.word(),
            name=self.fake.name(),
            email=self.fake.email(),
            phone_number='010-1234-1234',
            password='newpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 201)
        self.assertIn(b'success', response.data)

if __name__ == '__main__':
    unittest.main()
