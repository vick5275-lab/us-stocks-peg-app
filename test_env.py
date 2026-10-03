import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SIMFIN_API_KEY")

if api_key:
    print("อ่าน SIMFIN_API_KEY สำเร็จ")
    print(f"ความยาว API Key: {len(api_key)} ตัวอักษร")
else:
    print("ไม่พบ SIMFIN_API_KEY")