import pandas as pd
import yfinance as yf

# รายชื่อหุ้นครอบคลุมทุกกลุ่มอุตสาหกรรม
all_tickers = [
    # Semiconductors & Chips
    "NVDA",
    "TSM",
    "AVGO",
    "MU",
    "AMD",
    "INTC",
    "QCOM",
    "ASML",
    "ARM",
    "TXN",
    "MRVL",
    "ADI",
    "AMAT",
    "LRCX",
    "KLAC",
    "NXPI",
    "MCHP",
    "ON",
    "SWKS",
    "QRVO",
    "STM",
    # Big Tech & Software
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "NFLX",
    "ORCL",
    "ADBE",
    "CRM",
    "NOW",
    "UBER",
    "ABNB",
    "PLTR",
"VRT",
"VPG",
"CRDO",
"ALAB",
"ALAB",
"ARM",
"BABA",
"CBRS",
"CDNS",
"CRWV",
"FPS",
"INDI",
"LITE",
"MRVL",
"NET",
"OKLO",
"OSS",
"PLTR",
"STM",
"WDC",
"XPEV",
"AXON",
"COIN",
"FN",
"NTRA",
"OUST",
"PL",
"PANW",
"QNT",
"RDW",
"QCOM",
"QUBT",
"ROK",
"SNDK",
"ZS",
    # Financials & Banking
    "BRK-B",
    "JPM",
    "V",
    "MA",
    "BAC",
    "WFC",
    "GS",
    "MS",
    "C",
    "AXP",
    "BLK",
    # Consumer & Healthcare
    "WMT",
    "PG",
    "KO",
    "PEP",
    "COST",
    "MCD",
    "NKE",
    "SBUX",
    "TGT",
    "HD",
    "DIS",
    "JNJ",
    "UNH",
    "LLY",
    "ABBV",
    "PFE",
    "MRK",
    "TMO",
    "AMGN",
    # Energy & Industrials
    "XOM",
    "CVX",
    "COP",
    "SLB",
    "CAT",
    "DE",
    "HON",
    "UPS",
    "BA",
    "GE",
    "F",
    "GM",
    "FN",
    "SOFI",
]

print(f"กำลังดึงข้อมูลและอัปเดตสถิติหุ้นทั้งหมด {len(all_tickers)} ตัว...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    # ดึงราคาปัจจุบัน
    share_price = info.get("currentPrice") or info.get("regularMarketPrice")

    # ดึงค่า Forward PE ตัวที่อัปเดตจาก info
    forward_pe = info.get("forwardPE")

    # ดึงค่าประมาณการเติบโตระยะยาว (Growth Estimate) 3-5 ปี จาก analysts' estimate
    # โดยลองดึงจากหลายฟิลด์ที่ Yahoo ใช้เก็บค่าคาดการณ์
    growth_rate = None
    
    # พยายามดึงจากตาราง Analysis ถ้ามี
    try:
      analysis = stock.analysis
      if analysis is not None and "Growth" in analysis.index:
        growth_rate = analysis.loc["Growth"].iloc[
            -1
        ]  # ค่าเฉลี่ยคาดการณ์ล่าสุด
    except:
      pass

    # ถ้าไม่มี ให้ดึงจาก info ฟิลด์สำรองที่มักตรงกับหน้าเว็บ
    if not growth_rate or growth_rate == 0:
      growth_rate = (
          info.get("epsEstimateGrowth")
          or info.get("growthEst")
          or info.get("earningsGrowth")
      )

    # คำนวณค่า PEG สดๆ เพื่อความแม่นยำและสอดคล้อง
    if forward_pe and growth_rate:
      # แปลงสัดส่วนทศนิยมเป็นเปอร์เซ็นต์ (เช่น 0.248 -> 24.8 หรือถ้ามาเป็นเปอร์เซ็นต์อยู่แล้วให้ใช้เลย)
      g_percent = (
          growth_rate * 100 if abs(growth_rate) < 2.0 else growth_rate
      )

      if g_percent > 0:
        peg = forward_pe / g_percent
      else:
        peg = None
    else:
      peg = None
      g_percent = None

    # กรณีที่คำนวณไม่ได้ ให้ลองดึง pegRatio สำเร็จรูปมาเป็นตัวสำรองสุดท้าย
    if (not peg or peg <= 0) and forward_pe:
      peg = info.get("pegRatio")
      if peg and peg > 0 and forward_pe:
        g_percent = forward_pe / peg

    if forward_pe and peg and peg > 0 and g_percent:
      data.append({
          "Ticker": ticker,
          "Company": info.get("shortName", ticker),
          "Share_Price": share_price,
          "Forward_PE": forward_pe,
          "3-5Y_Growth_Est_%": g_percent,
          "Forward_PEG": peg,
      })
      print(f"สำเร็จ: {ticker} (PE: {forward_pe}, PEG: {peg:.2f})")
    else:
      print(f"ข้าม {ticker}: ข้อมูลไม่สมบูรณ์")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)
df = df.drop_duplicates(subset=["Ticker"])
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(f"\nบันทึกข้อมูลเรียบร้อย! ข้อมูลพร้อมใช้งาน {len(df)} ตัว")