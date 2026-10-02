# 🎮 FacePlay - Interactive WebAR & AI Mini-Game Platform

> โปรเจกต์ Full-Stack พัฒนาระบบเว็บแอปพลิเคชันมินิเกมรูปแบบใหม่ที่ผสานเทคโนโลยี Computer Vision (MediaPipe AI) เข้ากับสถาปัตยกรรม Microservices บน Docker และ FastAPI เพื่อการันตีเสถียรภาพและความสามารถในการพกพารuนข้ามแพลตฟอร์มอย่างแท้จริง

---

## 🎯 งานของเราคืองานอะไร? (Project Overview & Core Scope)
**FacePlay** ไม่ใช่เป็นเพียงเว็บไซต์เกมทั่วไป แต่เป็น **Interactive WebAR Mini-Game Platform** ที่ถูกออกแบบมาเพื่อลบข้อจำกัดของการทำเว็บแอปพลิเคชันแบบดั้งเดิม โดยงานของเราครอบคลุมสัดส่วนการทำงานหลัก 3 ส่วนด้วยกัน:

1. **Client-Side AI & WebAR Engine (หน้าบ้าน):** 
   - เปลี่ยนเว็บแอปพลิเคชันธรรมดาให้กลายเป็นแพลตฟอร์มเกมควบคุมด้วยใบหน้าแบบ Real-time โดยใช้ **MediaPipe Face Mesh** ทำงานร่วมกับ HTML5 Canvas และ JavaScript 
   - ผู้เล่นไม่ต้องติดตั้งซอฟต์แวร์หรือแอปพลิเคชันเสริมใดๆ เพียงเปิดกล้องเว็บแคม ระบบจะดึงโครงสร้างใบหน้า (Landmarks) มาคำนวณการขยับ เช่น การอ้าปากงับซูชิ, การโยกหัวหลบสิ่งกีดขวาง, หรือการยิ้มรับทรัพย์ เพื่อแปลงเป็นอินพุตควบคุมเกมแทนการใช้เมาส์หรือคีย์บอร์ด
2. **Robust Backend REST API (หลังบ้าน):** 
   - พัฒนาด้วย **FastAPI** ซึ่งเป็น Python Framework ที่เด่นเรื่องความเร็วสูง และรองรับ Asynchronous 
   - จัดการโครงสร้างข้อมูลด้วย **Pydantic Model** เพื่อทำ Auto-Validation ตรวจสอบความถูกต้องของ Type และเงื่อนไขของข้อมูลตั้งแต่วินาทีแรกที่ส่งเข้ามา 
   - ครอบคลุมชุดคำสั่งมาตรฐานระดับโปรดักชันรวม **11 Endpoints** แบ่งเป็นระบบ Authentication (ล็อกอิน, สมัครสมาชิก, ออกจากระบบ, เปลี่ยนรหัสผ่าน) และระบบ User Management (จัดการข้อมูลสมาชิก ดึงข้อมูลตัวเอง ค้นหา แก้ไข และลบข้อมูล)
3. **Containerized Architecture & Orchestration (ระบบจัดเก็บและจำลองสภาพแวดล้อม):** 
   - ออกแบบระบบฐานข้อมูลด้วย **PostgreSQL** และเชื่อมต่อผ่านสถาปัตยกรรมแบบแยกส่วน (Microservices-oriented)
   - ห่อหุ้มทุกเซอร์วิสด้วย **Dockerfile** และควบคุมการทำงานร่วมกันทั้งหมดผ่าน **Docker Compose** เพื่อแก้ปัญหาคลาสสิกอย่าง *"It works on my machine!"* ทำให้มั่นใจได้ว่าโค้ดชุดนี้จะรันได้ผลลัพธ์เหมือนกัน 100% ไม่ว่าจะรันบนเครื่องนักพัฒนาหรือบน Cloud Server[cite: 1]

---

## 💡 ทำไมถึงต้องทำโปรเจกต์นี้? (Motivation & Objective)
* **ก้าวข้ามข้อจำกัดของเว็บแอปแบบเดิม:** ในการเรียนรู้และพัฒนาซอฟต์แวร์ทั่วไป มักจบลงที่การทำเว็บฟอร์ม CRUD (Create, Read, Update, Delete) พื้นฐาน ทางผู้พัฒนาจึงต้องการยกระดับความท้าทายด้วยการนำเทคโนโลยีปัญญาประดิษฐ์ (AI) ที่ประมวลผลฝั่งเบราว์เซอร์มาผนวกเข้ากับระบบจัดการฐานข้อมูลหลังบ้านจริง
* **ตอบโจทย์การใช้งานจริงในอุตสาหกรรม:** จำลองรูปแบบการพัฒนาซอฟต์แวร์ยุคใหม่ที่แยกส่วน Frontend และ Backend ออกจากกันอย่างเด็ดขาด (Decoupled Architecture) สื่อสารผ่าน RESTful API และส่งมอบงานในรูปแบบ Container เพื่อให้ง่ายต่อการดูแลรักษาและการ Scale ระบบในอนาคต

---

## ⚖️ ทำไมถึงแตกต่าง? (Key Differentiators & Technical Choices)
เมื่อเปรียบเทียบกับโปรเจกต์เว็บทั่วไป FacePlay มีความแตกต่างและจุดเด่นเชิงวิศวกรรมซอฟต์แวร์ที่ชัดเจน:

* **ปฏิสัมพันธ์รูปแบบใหม่ (Zero-Friction AI Controller):** แทนที่จะจำกัดให้ผู้ใช้เล่นเกมผ่านคีย์บอร์ดหรือหน้าจอสัมผัส FacePlay ดึงความสามารถของโครงข่ายประสาทเทียม (Neural Networks) ผ่าน MediaPipe มาให้เบราว์เซอร์ผู้ใช้ประมวลผลภาพใบหน้าได้เองในเสี้ยววินาที ลดภาระการคำนวณฝั่งเซิร์ฟเวอร์
* **สถาปัตยกรรมแบบแยกกล่อง (Containerized Isolation):** การใช้ Docker Compose ช่วยจำลองเครือข่ายเสมือน (Compose Network) ทำให้เซอร์วิสเว็บแอป, API, และฐานข้อมูลมองเห็นและคุยกันได้ด้วยชื่อเซอร์วิสทันทีโดยไม่ต้องตั้งค่า IP Address ให้ยุ่งยาก[cite: 1] ป้องกันปัญหาความขัดแย้งของเวอร์ชันไลบรารีในเครื่องแต่ละคน[cite: 1]
* **การตรวจสอบข้อมูลอัตโนมัติ (Pydantic Schema Validation):** ลดการเขียนโค้ดดักจับ Error แบบเดิมๆ โดยให้ FastAPI และ Pydantic ทำหน้าที่ตรวจสอบความถูกต้อง คัดกรองข้อมูล และส่ง Status Code (เช่น 400, 422, 404) กลับไปให้อย่างแม่นยำ[cite: 1]

---

## 🛠️ Tech Stack รายละเอียด
* **Frontend & WebAR:** HTML5, Tailwind CSS, MediaPipe Face Mesh, JavaScript (Canvas API)
* **Backend API:** Python, FastAPI, Pydantic, Psycopg2[cite: 1]
* **Database:** PostgreSQL
* **Infrastructure & DevOps:** Docker, Docker Compose[cite: 1]

---

## 📂 Project Architecture Structure

Web_dev_project/
├── my-api/                  # Backend Service (FastAPI & PostgreSQL Connection)
│   ├── Dockerfile           # กำหนด Environment และคำสั่งรัน Uvicorn Server
│   ├── main.py              # บรรจุ 11 Endpoints ทั้ง Auth และ User Management
│   └── requirements.txt     # ระบุ Dependencies (FastAPI, Uvicorn, Psycopg2, etc.)
├── my-frontend/             # Frontend Service (Nginx & WebAR Client)
│   ├── Dockerfile           # คัดลอกไฟล์เว็บไซต์เข้าสู่ Nginx Web Server
│   ├── index.html           # หน้าจอ Login เข้าสู่ระบบ
│   ├── register.html        # หน้าจอสมัครสมาชิกพร้อมระบบเช็ก Username ซ้ำ
│   └── game.html            # หน้าจอหลัก Game Arena, MediaPipe AI และ Settings Modal
└── docker-compose.yml       # ไฟล์ควบคุมและจัดการ Multi-container Orchestration



วิธีการติดตั้งและรันระบบ (Quick Start)

1.ตรวจสอบความพร้อม: ติดตั้ง Docker Desktop และเปิดใช้งานให้เรียบร้อย (รองรับทั้ง Windows WSL2, macOS, และ Linux)[cite: 1]

2.ดาวน์โหลดหรือเปิดโฟลเดอร์โปรเจกต์: ไปที่ไดเรกทอรีหลักของโปรเจกต์ (Web_dev_project)

3.สั่งประกอบและรันระบบทั้งหมดด้วย Docker Compose:

docker compose up -d --build

4.เข้าใช้งานระบบผ่านเบราว์เซอร์:

    -หน้าเว็บหลัก (Login / Game): http://localhost:8080

    -เอกสารคู่มือ API อัตโนมัติ (Swagger UI): http://localhost:8000/docs (สามารถกด Try it out ทดสอบยิง Request ได้ทันที)[cite: 1]

สรุปรายการ API Endpoints ที่รองรับ

    -Authentication: POST /register, POST /login, POST /logout, POST /change-password

    -User Management: GET /me, GET /users/{id}, GET /users (รองรับ Pagination), PUT /users/{id}, DELETE /users/{id}, GET /check-username/{name}


สมาชิก
1.67160379 นายสุรศักดิ์ นึกรักษ์ 
2.67160326 นายชัชชนม์ โทสวนจิตร



![architecture](https://github.com/user-attachments/assets/c3412c3f-7c8b-439d-a1be-ae77609b4a97)

<img width="1920" height="1080" alt="Technology Stack Architecture" src="https://github.com/user-attachments/assets/d1d44d8a-9a2d-4722-ace4-b1101ef2794e" />


