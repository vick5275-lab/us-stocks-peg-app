import os
import pandas as pd
import simfin as sf
from dotenv import load_dotenv

# อ่าน API Key
load_dotenv()

api_key = os.getenv("SIMFIN_API_KEY")

if not api_key:
    raise RuntimeError("ไม่พบ SIMFIN_API_KEY ในไฟล์ .env")

# ตั้งค่า SimFin
sf.set_api_key(api_key)
sf.set_data_dir("./simfin_data")

# โหลดงบกำไรขาดทุนรายปี
income = sf.load_income(
    variant="annual",
    market="us"
)

# เปลี่ยน Ticker และ Report Date จาก Index เป็นคอลัมน์
df = income.reset_index()

# แปลงข้อมูลเป็นตัวเลข
df["Net Income (Common)"] = pd.to_numeric(
    df["Net Income (Common)"],
    errors="coerce"
)

df["Shares (Diluted)"] = pd.to_numeric(
    df["Shares (Diluted)"],
    errors="coerce"
)

# ตัดแถวที่ข้อมูลไม่ครบหรือจำนวนหุ้นเป็นศูนย์
df = df.dropna(
    subset=[
        "Ticker",
        "Report Date",
        "Net Income (Common)",
        "Shares (Diluted)"
    ]
)

df = df[df["Shares (Diluted)"] != 0].copy()

# คำนวณ Diluted EPS
df["Diluted EPS"] = (
    df["Net Income (Common)"] /
    df["Shares (Diluted)"]
)

# เรียงข้อมูลตามหุ้นและปี
df = df.sort_values(
    ["Ticker", "Report Date"]
)

# EPS ของปีก่อน
df["Previous EPS"] = (
    df.groupby("Ticker")["Diluted EPS"]
    .shift(1)
)

# คำนวณ EPS Growth แบบปีต่อปี
df["EPS Growth %"] = (
    (
        df["Diluted EPS"] /
        df["Previous EPS"]
    ) - 1
) * 100

# สำหรับ PEG ให้ใช้ Growth เฉพาะเมื่อ EPS เดิมและปัจจุบันเป็นบวก
valid_growth = (
    (df["Previous EPS"] > 0) &
    (df["Diluted EPS"] > 0) &
    (df["EPS Growth %"] > 0)
)

df["EPS Growth for PEG %"] = df["EPS Growth %"].where(
    valid_growth
)

# เลือกงบล่าสุดของหุ้นแต่ละตัว
latest = (
    df.sort_values(["Ticker", "Report Date"])
    .groupby("Ticker", as_index=False)
    .tail(1)
)

# เลือกคอลัมน์ที่ต้องการ
result = latest[
    [
        "Ticker",
        "Report Date",
        "Fiscal Year",
        "Net Income (Common)",
        "Shares (Diluted)",
        "Diluted EPS",
        "Previous EPS",
        "EPS Growth %",
        "EPS Growth for PEG %"
    ]
].copy()

# เรียงตาม Ticker
result = result.sort_values("Ticker")

# บันทึกเป็น CSV
result.to_csv(
    "us_latest_eps_growth.csv",
    index=False,
    encoding="utf-8-sig"
)

print("คำนวณ EPS และ EPS Growth สำเร็จ")
print("จำนวนหุ้น:", len(result))

print("\nตัวอย่างข้อมูล 20 รายการ:")
print(result.head(20).to_string(index=False))

print("\nสร้างไฟล์แล้ว: us_latest_eps_growth.csv")