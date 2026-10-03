import os
import pandas as pd
import simfin as sf
from dotenv import load_dotenv

# 1. อ่าน API Key
load_dotenv()
api_key = os.getenv("SIMFIN_API_KEY")

if not api_key:
    raise RuntimeError("ไม่พบ SIMFIN_API_KEY ในไฟล์ .env")

sf.set_api_key(api_key)
sf.set_data_dir("./simfin_data")

print("กำลังโหลดข้อมูล Derived Share Prices (P/E Ratios)...")

# 2. โหลด Derived Share Prices (มี P/E Ratio)
# หมายเหตุ: ชุดข้อมูลนี้อาจต้องใช้แพ็กเกจ SimFin+ หากฟรีอาจจำกัดการเข้าถึง
try:
    derived_prices = sf.load_derived_shareprices(
        variant="annual",
        market="us"
    )
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการโหลดแบบ annual ลองแบบ latest: {e}")
    derived_prices = sf.load_derived_shareprices(
        variant="latest",
        market="us"
    )

pe_df = derived_prices.reset_index()

print("คอลัมน์ใน derived_prices:")
print(pe_df.columns.tolist())

# ค้นหาคอลัมน์ P/E
pe_candidates = [
    "P/E Ratio",
    "Price to Earnings Ratio",
    "PE",
    "Price to Earnings"
]

pe_col = next((col for col in pe_candidates if col in pe_df.columns), None)

if not pe_col:
    # พยายามหาคอลัมน์ที่มีคำว่า 'Earnings' หรือ 'P/E'
    for col in pe_df.columns:
        if "P/E" in col or ("Price" in col and "Earnings" in col):
            pe_col = col
            break

if not pe_col:
    raise ValueError(
        f"ไม่พบคอลัมน์ P/E ในชุดข้อมูล กรุณาตรวจสอบชื่อคอลัมน์จากรายการข้างต้น"
    )

print(f"พบคอลัมน์ P/E คือ: {pe_col}")

# เลือกข้อมูล P/E ล่าสุดของแต่ละ Ticker
pe_df[pe_col] = pd.to_numeric(pe_df[pe_col], errors="coerce")

# หาคอลัมน์วันที่
date_col = next(
    (col for col in ["Report Date", "Date", "Publish Date"] if col in pe_df.columns),
    None
)

if date_col:
    latest_pe = (
        pe_df.dropna(subset=[pe_col])
        .sort_values(["Ticker", date_col])
        .groupby("Ticker", as_index=False)
        .tail(1)
    )
else:
    latest_pe = pe_df.dropna(subset=[pe_col]).groupby("Ticker", as_index=False).tail(1)

# 3. โหลดไฟล์ EPS Growth ที่ทำไว้ก่อนหน้า
eps_df = pd.read_csv("us_latest_eps_growth.csv")

# 4. รวมข้อมูล EPS Growth และ P/E เข้าด้วยกัน
merged = pd.merge(
    eps_df,
    latest_pe[["Ticker", pe_col]],
    on="Ticker",
    how="inner"
)

# เปลี่ยนชื่อคอลัมน์ P/E ให้เป็นมาตรฐาน
merged = merged.rename(columns={pe_col: "PE_Ratio"})

# 5. คำนวณค่า PEG
# สูตร: PEG = P/E / EPS Growth % (ใช้ค่าที่เป็นบวกและผ่านเกณฑ์)
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

# จัดเรียงคอลัมน์และข้อมูล
final_result = merged[
    [
        "Ticker",
        "Report Date",
        "Fiscal Year",
        "Diluted EPS",
        "Previous EPS",
        "EPS Growth for PEG %",
        "PE_Ratio",
        "PEG"
    ]
].copy()

final_result = final_result.sort_values("PEG")

# บันทึกเป็นไฟล์ CSV สุดท้าย
final_result.to_csv(
    "us_stocks_final_peg.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nคำนวณค่า PEG สำเร็จ!")
print(f"จำนวนหุ้นที่มีข้อมูล PEG ทั้งหมด: {final_result['PEG'].notna().sum()} ตัว")
print("\nตัวอย่างหุ้นที่มีค่า PEG (เรียงจากน้อยไปมาก):")
print(final_result.dropna(subset=["PEG"]).head(15).to_string(index=False))

print("\nบันทึกไฟล์เรียบร้อย: us_stocks_final_peg.csv")