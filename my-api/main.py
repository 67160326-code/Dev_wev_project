from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@db:5432/mydb")

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    retries = 5
    for attempt in range(retries):
        conn = None
        cursor = None
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scores (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    game_id VARCHAR(50) NOT NULL,
                    score INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                -- การสร้าง Composite Index สำหรับ Leaderboard (game_id, score DESC)
                CREATE INDEX IF NOT EXISTS idx_scores_game_score ON scores (game_id, score DESC);
                CREATE INDEX IF NOT EXISTS idx_scores_score_desc ON scores (score DESC);
            """)
            conn.commit()
            print("Database initialized successfully")
            return
        except Exception as e:
            print(f"Error connecting to database (attempt {attempt+1}/{retries}): {e}")
            time.sleep(2)
        finally:
            if cursor:
                try: cursor.close()
                except: pass
            if conn:
                try: conn.close()
                except: pass

@app.on_event("startup")
def startup_event():
    init_db()

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

class UserUpdate(BaseModel):
    username: str
    password: str

class ScoreSubmit(BaseModel):
    username: str
    game_id: str
    score: int


# ==========================================
# 1. Authentication (ล็อกอิน/สมัคร)
# ==========================================

@app.post("/register")
def register(user: UserCreate):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username นี้ถูกใช้งานแล้ว")
        
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user.username, user.password))
        conn.commit()
        return {"message": "สมัครสมาชิกสำเร็จ!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.post("/login")
def login(user: UserCreate):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user.username, user.password))
        db_user = cursor.fetchone()
        
        if not db_user:
            raise HTTPException(status_code=400, detail="Username หรือ Password ไม่ถูกต้อง")
            
        return {"message": "เข้าสู่ระบบสำเร็จ!", "username": db_user["username"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.post("/logout")
def logout():
    return {"message": "ออกจากระบบสำเร็จ"}

@app.post("/change-password")
def change_password(data: ChangePasswordRequest):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (data.username, data.old_password))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=400, detail="รหัสผ่านเดิมไม่ถูกต้อง")
            
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (data.new_password, data.username))
        conn.commit()
        return {"message": "เปลี่ยนรหัสผ่านสำเร็จ"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ==========================================
# 2. User Management (จัดการข้อมูล)
# ==========================================

@app.get("/me")
def get_me(username: str):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="ไม่พบ User นี้")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.get("/users")
def get_all_users(limit: int = 10, offset: int = 0):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username FROM users ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
        users = cursor.fetchall()
        return {"users": users, "limit": limit, "offset": offset}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = %s, password = %s WHERE id = %s", (user.username, user.password, user_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบ User ID ที่ต้องการแก้ไข")
        conn.commit()
        return {"message": f"อัปเดตข้อมูล User ID {user_id} สำเร็จ"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="ไม่พบ User ID ที่ต้องการลบ")
        conn.commit()
        return {"message": f"ลบ User ID {user_id} สำเร็จ"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.get("/check-username/{name}")
def check_username(name: str):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (name,))
        exists = cursor.fetchone()
        
        if exists:
            return {"available": False, "message": "Username นี้ถูกใช้งานแล้ว"}
        return {"available": True, "message": "Username นี้สามารถใช้งานได้"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ==========================================
# 3. Leaderboard System (ระบบตารางคะแนน)
# ==========================================

@app.post("/scores")
def submit_score(data: ScoreSubmit):
    if data.score < 0:
        raise HTTPException(status_code=400, detail="คะแนนต้องไม่ติดลบ")
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            "INSERT INTO scores (username, game_id, score) VALUES (%s, %s, %s) RETURNING id, username, game_id, score, created_at",
            (data.username, data.game_id, data.score)
        )
        new_score = cursor.fetchone()
        conn.commit()
        return {"message": "บันทึกคะแนนสำเร็จ!", "data": new_score}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.get("/leaderboard")
def get_leaderboard(game_id: str = None, limit: int = 10):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if game_id and game_id != "all":
            cursor.execute("""
                SELECT username, game_id, MAX(score) as high_score, MAX(created_at) as latest_date
                FROM scores
                WHERE game_id = %s
                GROUP BY username, game_id
                ORDER BY high_score DESC
                LIMIT %s
            """, (game_id, limit))
        else:
            cursor.execute("""
                SELECT username, MAX(score) as high_score, COUNT(id) as total_games, MAX(created_at) as latest_date
                FROM scores
                GROUP BY username
                ORDER BY high_score DESC
                LIMIT %s
            """, (limit,))
        leaderboard = cursor.fetchall()
        return {"leaderboard": leaderboard, "game_id": game_id or "all"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.get("/my-scores")
def get_my_scores(username: str):
    conn = None
    cursor = None
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT game_id, MAX(score) as best_score, COUNT(id) as played_count
            FROM scores
            WHERE username = %s
            GROUP BY game_id
            ORDER BY best_score DESC
        """, (username,))
        scores = cursor.fetchall()
        return {"username": username, "scores": scores}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor: cursor.close()
        if conn: conn.close()