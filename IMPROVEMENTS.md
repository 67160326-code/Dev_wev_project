# 📋 บันทึกการปรับปรุงและพัฒนาเพิ่มเติม (Project Improvements & Changelog)

เอกสารฉบับนี้จัดทำขึ้นเพื่อสรุปรายการปรับปรุง แก้ไข และฟีเจอร์ใหม่ที่พัฒนาเพิ่มเติมจาก **โค้ดตั้งต้น (Initial Commit จาก Git)** โดยแบ่งตามแต่ละส่วนของโปรเจกต์อย่างชัดเจน

---

## 📊 ตารางสรุปภาพรวมการเปลี่ยนแปลง (Summary Matrix)

| ส่วนของโปรเจกต์ (Component) | โค้ดตั้งต้นจาก Git | สิ่งที่ปรับปรุงและพัฒนาเพิ่มขึ้นมา |
| :--- | :--- | :--- |
| **1. Backend & Database** (`my-api/main.py`) | มีเฉพาะตาราง `users` และ 11 API Endpoints สำหรับ Auth/User | <ul><li>สร้างตาราง `scores` บันทึกประวัติคะแนน</li><li>ทำ **Composite B-Tree Index** เร่งความเร็ว Leaderboard</li><li>เพิ่ม 3 Endpoints ใหม่สำหรับระบบคะแนน</li><li>ปรับปรุง Pagination ด้วย Primary Key Index</li></ul> |
| **2. Game Engine & WebAR** (`my-frontend/game.html`) | มี 3 มินิเกมพื้นฐาน, บังคับใช้กล้องเว็บแคมอย่างเดียว, ไม่มีเสียง | <ul><li>**เพิ่ม 2 มินิเกมใหม่** (ทำท่าโจทย์ 🎭 และกระโดด 🦘)</li><li>ระบบ **100% Face & Physical Controls** (บังคับด้วยใบหน้าและท่าทางจริงเท่านั้น)</li><li>ระบบเสียงสังเคราะห์ **Web Audio API** (ไม่ต้องใช้ไฟล์ MP3)</li><li>ระบบ Visual Effects (Screen Shake, Particles, Floating Text)</li><li>ปรับไอเทม/สิ่งกีดขวางเป็น **High-Contrast Badges**</li><li>เพิ่มหน้าต่าง **ตารางอันดับคะแนน (Leaderboard Modal)**</li><li>แก้ไข Syntax Error และเพิ่ม **Camera Fallback**</li></ul> |
| **3. Responsive UI** | หน้าจอไม่พอดีอุปกรณ์ | <ul><li>รองรับ **Auto-Responsive** ปรับขนาด UI ให้พอดีกับอุปกรณ์ของผู้ใช้อัตโนมัติ 100%</li></ul> |
| **4. Auth & UI Design System** (`index.html`, `register.html`) | ดีไซน์สีฉูดฉาดแบบเรียบง่าย ปุ่มนิ่งเฉยเวลาคลิก | <ul><li>ยกเครื่องเป็นดีไซน์ **Minimal Cyber-Arcade** คุมโทน Obsidian</li><li>ปุ่มและแผ่นการ์ดสไตล์ **3D Tactile** มีมิติการกด</li><li>เพิ่มการแสดงสถานะกำลังโหลดบนปุ่ม ป้องกันการกดซ้ำ</li><li>ปรับปรุง `API_URL` ให้ยืดหยุ่นต่อทุก Hostname และโปรโตคอล</li></ul> |

---

## 🗄️ ส่วนที่ 1: ระบบฐานข้อมูลและ Backend API (`my-api/main.py`)

### 1.1 การสร้างตารางคะแนนใหม่ (`scores`)
เพิ่มตารางใหม่บน PostgreSQL เพื่อรองรับการเก็บสถิติคะแนนของผู้เล่นแยกตามแต่ละเกม:
```sql
CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    game_id VARCHAR(50) NOT NULL,
    score INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 1.2 การประยุกต์ใช้ความรู้จาก Indexing Lab
- **Composite Index สำหรับ Leaderboard**:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_scores_game_score ON scores (game_id, score DESC);
  ```
  ช่วยให้การ Query จัดอันดับคะแนนสูงสุดแยกตามประเภทเกม เช่น `WHERE game_id = 'sushi' ORDER BY score DESC LIMIT 10` ทำงานได้เร็วระดับ $O(\log N)$ โดยฐานข้อมูลไม่ต้องทำ Sequential Scan หรือ Sort ในหน่วยความจำ
- **Single-Column Index**:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_scores_score_desc ON scores (score DESC);
  ```
  รองรับการดึงอันดับคะแนนรวมทุกเกมแบบรวดเร็ว
- **Optimized Pagination**:
  ปรับคำสั่ง `SELECT id, username FROM users ORDER BY id LIMIT %s OFFSET %s` ให้ระบุ `ORDER BY id` เพื่อให้ฐานข้อมูลใช้ B-Tree Index ของ Primary Key โดยตรง

### 1.3 การเพิ่ม 3 Endpoints ใหม่สำหรับระบบคะแนน
- `POST /scores`: บันทึกคะแนนหลังจบเกม พร้อมตรวจสอบเงื่อนไขความถูกต้องด้วย Pydantic (`score >= 0`)
- `GET /leaderboard`: ดึงตารางอันดับคะแนนสูงสุด รองรับพารามิเตอร์ `game_id` และ `limit`
- `GET /my-scores`: ดูประวัติสถิติและคะแนนสูงสุดส่วนตัวของผู้ใช้แต่ละคน

---

## 🎮 ส่วนที่ 2: หน้าสนามเกมและ WebAR AI (`my-frontend/game.html`)

### 2.1 เพิ่ม 2 มินิเกมใหม่ (รวมเป็น 5 โหมดเกม)
จากเดิมที่มีเพียง 3 เกม (กินซูชิ 🍣, หลบงาน 📁, ยิ้มรับทรัพย์ 💰) ได้พัฒนาเพิ่มเติมอีก 2 เกม:
1. 🎭 **ทำท่าโจทย์ (Pose Matcher)**:
   - ระบบสุ่มท่าทางโจทย์แบบไดนามิก เช่น อ้าปาก, ฉีกยิ้มกว้าง, เอียงคอซ้าย, เอียงคอขวา, ทำปากจู๋, เงยหน้า
   - มีหลอดเวลาจำกัด และตรวจจับองศาใบหน้า (Facial Landmarks) ผ่าน MediaPipe เพื่อให้คะแนน
2. 🦘 **กระโดดข้ามรั้ว (Jump & Run)**:
   - เกมแนว Endless Runner มีสิ่งกีดขวางภาคพื้นดินพุ่งเข้ามา และมีไอเทมดาวลอยอยู่กลางอากาศ
   - ตรวจจับการกระโดดจริงด้วยการขยับศีรษะผ่านเส้น Baseline หรือกด Spacebar/แตะหน้าจอ
   - มีมาตรวัดความสูงการกระโดด (Jump Meter) และสัญญาณเตือนอันตรายล่วงหน้า (`⚠️ INCOMING!`)

### 2.2 ระบบควบคุมด้วย AI แบบ 100% (Pure AI Controls)
- **Face AI & Physical Movement**: ยกเลิกระบบควบคุมด้วยการคลิกหรือหน้าจอสัมผัสทั้งหมด เพื่อให้ผู้เล่นเล่นเกมด้วยใบหน้าอย่างเดียว และในส่วนของเกมกระโดดจะใช้การจับการกระโดดด้วยร่างกายจริงเท่านั้น

### 2.3 การปรับปรุงการมองเห็นไอเทมและสิ่งกีดขวาง (Visual Clarity)
- ปรับเปลี่ยนจากอิโมจิลอยแบบโปร่งใส มาเป็น **High-Contrast Badges**: มีกรอบวงกลมทึบและแสงเรืองรอบนอก (Outer Glow)
- ไอเทมอันตรายมีป้ายกำกับชัดเจน (`⚠️ DANGER`) ทำให้มองเห็นและเล่นได้ง่ายบนทุกสภาพแสงของกล้อง

### 2.4 ระบบเสียงสังเคราะห์ (Web Audio API Synthesizer)
- พัฒนา Audio Synthesizer ขึ้นมาเองโดยใช้ Web Audio API (สร้างคลื่นเสียง Sine, Triangle, Sawtooth แบบเรียลไทม์)
- **Zero External Assets**: ไม่ต้องดาวน์โหลดไฟล์ `.mp3` แม้แต่ไฟล์เดียว โหลดไว 0 วินาที ไม่มีปัญหาไฟล์หาย (404) หรือติด CORS
- มีเสียงกดปุ่ม, เสียงเก็บแต้ม, เสียงคอมโบไต่ระดับ, เสียงชนสิ่งกีดขวาง, เสียงนับถอยหลัง 3-2-1-GO และเสียง Game Over พร้อมปุ่มเปิด/ปิดเสียง (Mute/Unmute)

### 2.5 ระบบ Dynamic Visual Effects (VFX)
- **Screen Shake & Damage Vignette**: สั่นหน้าจอและกะพริบขอบแดงเมื่อชนสิ่งกีดขวาง
- **Particle Explosion**: อนุภาคแสงกระจายตัวเมื่อได้รับคะแนน
- **Floating Score Text**: ตัวเลขคะแนนลอยขึ้นตามจุดที่เกิด Action
- **Combo Streak Badge**: ป้ายไฟนับจำนวนคอมโบต่อเนื่องเปล่งแสงแอนิเมชัน

### 2.6 ระบบตารางคะแนนในเกม (In-Game Leaderboard Modal)
- หน้าต่าง Popup ดูอันดับคะแนนแบบ Real-time พร้อมแท็บเลือกดูคะแนนแยกตามแต่ละมินิเกม
- แสดงเหรียญรางวัล 🥇, 🥈, 🥉 และ Rank Badge ของผู้เล่น
- บันทึกคะแนนลงเซิร์ฟเวอร์อัตโนมัติเมื่อ Game Over

### 2.7 การแก้ปัญหาความเสถียร (Bug Fixes & Resilience)
- **แก้ปัญหา Syntax Error (Unmatched Brace)**: ล้างโค้ดฟังก์ชันซ้ำซ้อนใน `game.html` แก้ปัญหาที่เคยกดปุ่มแล้วไม่ทำงาน
- **Graceful Camera Fallback**: หากอุปกรณ์ไม่มีกล้อง หรือยังไม่อนุญาตสิทธิ์กล้อง ระบบจะไม่ค้างหน้าโหลด แต่จะสลับเข้าสู่โหมด Touch/Keyboard ทันที
- **Live Reload Frontend (Docker Volume)**: เพิ่ม Volume Mapping สำหรับ `my-frontend` ใน `docker-compose.yml` เพื่อให้การแก้ไขโค้ดฝั่งหน้าบ้านอัปเดตแบบเรียลไทม์โดยไม่ต้อง Build Image ใหม่ทุกครั้ง
- **Port Conflict Resolution**: เปลี่ยนพอร์ตของ Frontend จาก `8080` เป็น `3000` เพื่อหลีกเลี่ยงการชนกับ Service อื่นๆ ในระบบ (เช่น Python หรือ Jenkins ที่มักจองพอร์ต 8080)

---

## 📱 ส่วนที่ 3: ระบบการแสดงผลอัตโนมัติ (Auto-Responsive UI)

### 3.1 Seamless Auto-Fit Design
- ปรับเปลี่ยนให้ UI ปรับขนาดให้เหมาะกับอุปกรณ์ของผู้ใช้อัตโนมัติ (Auto-Responsive) เต็มรูปแบบ โดยไม่ต้องสลับโหมดจำลองเอง
- โครงสร้างแอปใช้ `100dvh` ทำให้เกมแสดงผลแบบ Fullscreen พอดีเป๊ะเสมือน Native App ไม่ว่าจะเปิดในคอมพิวเตอร์หรือสมาร์ทโฟน

---

## 🎨 ส่วนที่ 4: หน้าเข้าสู่ระบบและสมัครสมาชิก (`index.html` & `register.html`)

### 4.1 ปรับปรุง UI ให้เป็น Minimal Cyber-Arcade
- คุมโทนสี Dark Obsidian (`#09090b` ถึง `#181822`) สบายตาและทันสมัย
- การ์ดและปุ่มกดสไตล์ **3D Tactile**: มีขอบหนา แสงเงา Specular และแอนิเมชันยุบตัวตามแรงกด

### 4.2 การตอบสนองบนปุ่ม (Interactive Feedback)
- เพิ่มข้อความแสดงสถานะทันทีเมื่อกดปุ่ม (เช่น `"กำลังเข้าสู่ระบบ..."`, `"กำลังสร้างบัญชีผู้ใช้..."`) ป้องกันการกดซ้ำซ้อนและแจ้งสถานะชัดเจน

### 4.3 ปรับปรุงความยืดหยุ่นของ `API_URL`
- ปรับตรรกะการตรวจสอบ URL ของหลังบ้านให้อัตโนมัติ:
  ```javascript
  const API_URL = (!window.location.hostname || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:')
      ? "http://localhost:8000"
      : `${window.location.protocol === 'https:' ? 'https:' : 'http:'}//${window.location.hostname}:8000`;
  ```
  รองรับทั้งการเข้าผ่าน `localhost:8080`, เข้าผ่านไอพีวง LAN บนมือถือ, และการเปิดทดสอบตรงผ่านไฟล์ (`file:///`)
