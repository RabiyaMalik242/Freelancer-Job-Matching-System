import pyodbc

class Database:
    def __init__(self):
        try:
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 18 for SQL Server};'
                'SERVER=DESKTOP-63LBVQG\\SQLEXPRESS;'
                'DATABASE=FreelancerDB;'
                'Trusted_Connection=yes;'
                'Encrypt=no;'
            )
            self.cursor = self.conn.cursor()
            self.initialize_tables()
            print("DB Connected Successfully")
        except Exception as e:
            raise Exception(f"Database Connection Failed: {e}")

    # ------------------------------
    # Initialize tables
    # ------------------------------
    def initialize_tables(self):
        try:
            self.cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Users')
                CREATE TABLE Users (
                    id INT IDENTITY PRIMARY KEY,
                    fullname VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    password VARCHAR(100),
                    role VARCHAR(20)
                )
            """)

            self.cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Jobs')
                CREATE TABLE Jobs (
                    id INT IDENTITY PRIMARY KEY,
                    title VARCHAR(200),
                    description TEXT,
                    budget INT,
                    category VARCHAR(50),
                    client_email VARCHAR(100)
                )
            """)

            self.cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name='Applications')
                CREATE TABLE Applications (
                    id INT IDENTITY PRIMARY KEY,
                    job_id INT,
                    freelancer_email VARCHAR(100),
                    freelancer_name VARCHAR(100),
                    skills VARCHAR(200)
                )
            """)

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Table Initialization Failed: {e}")

    # ------------------------------
    # CRUD FUNCTIONS WITH ERROR HANDLING
    # ------------------------------
    def register_user(self, fullname, email, password, role):
        try:
            self.cursor.execute("""
                INSERT INTO Users(fullname, email, password, role)
                VALUES (?, ?, ?, ?)
            """, (fullname, email, password, role))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"User Registration Failed: {e}")

    def validate_login(self, email, password, role):
        try:
            self.cursor.execute("""
                SELECT * FROM Users
                WHERE email = ? AND password = ? AND role = ?
            """, (email, password, role))
            return self.cursor.fetchone()
        except Exception as e:
            raise Exception(f"Login Query Failed: {e}")

    def insert_job(self, title, desc, budget, category, client_email):
        try:
            self.cursor.execute("""
                INSERT INTO Jobs(title, description, budget, category, client_email)
                VALUES (?, ?, ?, ?, ?)
            """, (title, desc, budget, category, client_email))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Insert Job Failed: {e}")

    def get_jobs(self):
        try:
            self.cursor.execute("SELECT * FROM Jobs")
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Get Jobs Failed: {e}")

    def get_all_users(self):
        try:
            self.cursor.execute("SELECT id, fullname, email, role FROM Users")
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Get Users Failed: {e}")

    def get_all_applications(self):
        try:
            self.cursor.execute("""
                SELECT job_id, freelancer_email, freelancer_name, skills
                FROM Applications
            """)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Get All Applications Failed: {e}")

    def delete_job(self, job_id):
        try:
            self.cursor.execute("DELETE FROM Applications WHERE job_id=?", (job_id,))
            self.cursor.execute("DELETE FROM Jobs WHERE id=?", (job_id,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Delete Job Failed: {e}")

    def delete_user(self, user_id):
        try:
            # Check if user exists
            self.cursor.execute("SELECT email FROM Users WHERE id=?", (user_id,))
            row = self.cursor.fetchone()

            if not row:
                return False   # user does NOT exist, nothing to delete

            email = row[0]

            # delete applications of user's jobs
            self.cursor.execute("""
                DELETE FROM Applications 
                WHERE job_id IN (SELECT id FROM Jobs WHERE client_email=?)
            """, (email,))

            # delete their jobs
            self.cursor.execute("DELETE FROM Jobs WHERE client_email=?", (email,))

            # delete user
            self.cursor.execute("DELETE FROM Users WHERE id=?", (user_id,))
            self.conn.commit()

            return True   # success

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Delete User Failed: {e}")
        

    def get_user_by_id(self, user_id):
        self.cursor.execute("""
            SELECT id, fullname, email, password, role
            FROM Users
            WHERE id=?
        """, (user_id,))
        return self.cursor.fetchone()
    

    def update_user(self, user_id, fullname, email, password, role):
        try:
            self.cursor.execute("""
                UPDATE Users
                SET fullname=?, email=?, password=?, role=?
                WHERE id=?
            """, (fullname, email, password, role, user_id))

            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Update User Failed: {e}")


    def insert_application(self, job_id, email, name, skills):
        try:
            self.cursor.execute("""
                INSERT INTO Applications(job_id, freelancer_email, freelancer_name, skills)
                VALUES (?, ?, ?, ?)
            """, (job_id, email, name, skills))
            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Apply Job Failed: {e}")

    def get_job_title(self, job_id):
        try:
            self.cursor.execute("SELECT title FROM Jobs WHERE id=?", (job_id,))
            row = self.cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            raise Exception(f"Get Job Title Failed: {e}")

    def get_applications(self, job_id):
        try:
            self.cursor.execute("""
                SELECT freelancer_email, freelancer_name, skills
                FROM Applications
                WHERE job_id = ?
            """, (job_id,))
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Get Applications Failed: {e}")

# print("DB Connected Successfully")
