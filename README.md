# financial-etl-pipeline (Work in Progress)

โปรเจกต์ฝึกเขียน **Financial ETL Pipeline ด้วยมือตัวเอง** (Python + Pandas) เพื่อดึงข้อมูลราคาหุ้น ตรวจสอบ/ทำความสะอาดข้อมูล และโหลดลงฐานข้อมูลสำหรับนำไป query ต่อ

> **สถานะปัจจุบัน: ยังไม่เสร็จ (Work in Progress)** — ทำเสร็จเฉพาะส่วน `Extract` และ `Transform` ส่วน `Load` และตัวรันหลัก (`main.py`) ยังว่างอยู่

---

## สถานะแต่ละส่วน (ตามโค้ดจริง)

| โมดูล | ไฟล์ | สถานะ | สิ่งที่ทำได้ตอนนี้ |
| :--- | :--- | :--- | :--- |
| Extract | `src/extract.py` | เสร็จขั้นต้น | ดึงข้อมูล OHLCV จาก `yfinance`, แปลงวันที่เป็น UTC `YYYY-MM-DD`, log ลง `logs/etl.log`, ข้าม ticker ที่พังได้โดยไม่แครชทั้งรอบ |
| Transform | `src/transform.py` | เสร็จขั้นต้น | แยกแถวเสีย (`NaN`, `close <= 0`, ซ้ำ `(ticker, trade_date)`, `high < low`) ออกไปเก็บที่ `data/rejected_rows.csv` แล้วคำนวณ `daily_return` กับ `sma_20` |
| Load | `src/load.py` | **ยังว่าง** | รอเขียนโค้ดสร้างตารางและ upsert ลง SQLite |
| Orchestrator | `main.py` | **ยังว่าง** | รอเชื่อม `extract -> transform -> load` เข้าด้วยกัน |
| Tests | `tests/` | **ยังไม่มี** | รอเขียน unit test ด้วย `pytest` |

---

## วิธีรันทดสอบส่วนที่มีตอนนี้

```powershell
python -m pip install -r requirements.txt

# ทดสอบดึงข้อมูลตัวอย่าง (AAPL, MSFT, BBL.BK, INVALID123)
python src/extract.py

# ทดสอบ transform + แยกแถวเสียบนข้อมูลจำลองในไฟล์
python src/transform.py
```

---

## แนวทางพัฒนาต่อ (ทำเองทีละขั้น)

1. **เขียน `src/load.py` (SQLite + Idempotent Upsert):** สร้างตาราง `daily_prices` ที่มี `PRIMARY KEY (ticker, trade_date)` และใช้ `INSERT OR REPLACE` / `ON CONFLICT DO UPDATE` เพื่อรันซ้ำได้โดยข้อมูลไม่เบิ้ล
2. **เชื่อมท่อใน `main.py`:** รับรายการ ticker และช่วงเวลาผ่าน CLI (`argparse`) รันครบ `Extract -> Transform -> Load` พร้อมสรุปจำนวนแถวที่ผ่าน/ถูกคัดออก
3. **เขียน SQL Queries ตัวอย่าง (`sql/analytics.sql`):** เช่น หา Top movers, rolling average, cumulative return ด้วย Window Functions (`LAG`, `AVG() OVER`, `RANK`)
4. **เพิ่ม Unit Tests (`tests/`):** ทดสอบเคสข้อมูลเสีย, การรันซ้ำ (idempotency), และค่า `daily_return` / `sma_20` เทียบกับค่าที่คำนวณมือ
5. **แยก config ออกจากโค้ด:** ย้ายรายชื่อ ticker และ path ฐานข้อมูลไปไว้ใน CLI arguments หรือไฟล์ config
