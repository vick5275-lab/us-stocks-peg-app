import os
import simfin as sf
from dotenv import load_dotenv

# อ่าน API Key จากไฟล์ .env
load_dotenv()

api_key = os.getenv("SIMFIN_API_KEY")

if not api_key:
    raise RuntimeError("ไม่พบ SIMFIN_API_KEY ในไฟล์ .env")

# ตั้งค่า SimFin
sf.set_api_key(api_key)
sf.set_data_dir("./simfin_data")

print("กำลังโหลด Income Statements ของหุ้นสหรัฐ...")

# โหลดงบกำไรขาดทุนรายปี
income = sf.load_income(
    variant="annual",
    market="us", refresh_days=1
)

print("\nโหลดข้อมูลสำเร็จ")
print("จำนวนแถวและคอลัมน์:", income.shape)

print("\nชื่อ Index:")
print(income.index.names)

print("\nชื่อคอลัมน์ทั้งหมด:")
for column in income.columns:
    print("-", column)

print("\nตัวอย่างข้อมูล 5 แถวแรก:")
print(income.head())