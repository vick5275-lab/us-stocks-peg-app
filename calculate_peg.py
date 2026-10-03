import os
import pandas as pd
import simfin as sf
from dotenv import load_dotenv

# 1. โหลด API Key
load_dotenv()
api_key = os.getenv("SIMFIN_API_KEY")

if not api_key:
    raise RuntimeError("ไม่พบ SIMFIN_API_KEY ในไฟล์ .env")

sf.set_api_key(api_key)
sf.set_data_dir("./simfin_data")

print("กำลังโหลดข้อมูล Share Prices พื้นฐาน...")

# 2. โหลด Share Prices แบบรายวันหรือล่าสุด (ฟรี)
try:
    prices = sf.load_shareprices(variant="daily", market="us")
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการโหลดราคา ลองแบบ latest: {e}")
    prices = sf.load_shareprices(variant="latest", market="us")

prices_df = prices.reset_index()

# หาคอลัมน์ราคาปิด (Close Price)
price_col = next((col for col in ["Close", "Adj. Close", "Share Price"] if col in prices_df.columns), None)
if not price_col:
    price_col = prices_df.columns[-1] # เลือกคอลัมน์สุดท้ายเผื่อเป็นราคา

print(f"ใช้คอลัมน์ราคาคือ: {price_col}")

# กรองเอาเฉพาะข้อมูลล่าสุดของแต่ละ Ticker
date_col = next((col for col in ["Date", "Publish Date"] if col in prices_df.columns), None)
if date_col:
    latest_prices = prices_df.dropna(subset=[price_col]).sort_values(["Ticker", date_col]).groupby("Ticker", as_index=False).tail(1)
else:
    latest_prices = prices_df.dropna(subset=[price_col]).groupby("Ticker", as_index=False).tail(1)

# 3. โหลดไฟล์ EPS Growth ที่คำนวณไว้ก่อนหน้า
eps_df = pd.read_csv("us_latest_eps_growth.csv")

# 4. รวมข้อมูล EPS และ ราคาหุ้น
merged = pd.merge(
    eps_df,
    latest_prices[["Ticker", price_col]],
    on="Ticker",
    how="inner"
)

merged = merged.rename(columns={price_col: "Share_Price"})
merged["Share_Price"] = pd.to_numeric(merged["Share_Price"], errors="coerce")
merged["Diluted EPS"] = pd.to_numeric(merged["Diluted EPS"], errors="coerce")

# 5. คำนวณ P/E Ratio (Price / EPS)
merged["PE_Ratio"] = merged["Share_Price"] / merged["Diluted EPS"]

# 6. คำนวณค่า PEG (PE / EPS Growth %)
valid_mask = (
    merged["EPS Growth for PEG %"].notna() &
    (merged["EPS Growth for PEG %"] > 0) &
    merged["PE_Ratio"].notna() &
    (merged["PE_Ratio"] > 0)
)

merged["PEG"] = pd.NA
merged.loc[valid_mask, "PEG"] = (
    merged.loc[valid_mask, "PE_Ratio"] /
    merged.loc[valid_mask, "EPS Growth for PEG %"]
)

# จัดรูปแบบผลลัพธ์
final_result = merged[
    [
        "Ticker",
        "Report Date",
        "Fiscal Year",
        "Diluted EPS",
        "Share_Price",
        "EPS Growth for PEG %",
        "PE_Ratio",
        "PEG"
    ]
].copy()

final_result = final_result.sort_values("PEG")

# บันทึกไฟล์ CSV สุดท้าย
final_result.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print("\nคำนวณค่า PEG สำเร็จ!")
print(f"จำนวนหุ้นที่มีข้อมูล PEG ทั้งหมด: {final_result['PEG'].notna().sum()} ตัว")
print(final_result.dropna(subset=["PEG"]).head(10).to_string(index=False))
print("\nบันทึกไฟล์เรียบร้อย: us_stocks_final_peg.csv")