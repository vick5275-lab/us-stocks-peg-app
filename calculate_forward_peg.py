import pandas as pd
import yfinance as yf

# รายชื่อหุ้นยอดนิยมในพอร์ต
all_tickers = [
    # Technology
    "AAPL",
    "MSFT",
    "NVDA",
    "AVGO",
    "ORCL",
    "ADBE",
    "CRM",
    "AMD",
    "ACN",
    "CSCO",
    "IBM",
    "INTC",
    "QCOM",
    "TXN",
    "AMAT",
    "MU",
    "LRCX",
    "NOW",
    "PANW",
    "SNPS",
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
    # Communication Services
    "GOOGL",
    "META",
    "NFLX",
    "DIS",
    "CMCSA",
    "VZ",
    "T",
    "TMUS",
"DDOG",

    # Consumer Discretionary
    "AMZN",
    "TSLA",
    "HD",
    "MCD",
    "NKE",
    "SBUX",
    "LOW",
    "BKNG",
    "TJX",
    "CMG",
    "MAR",
    "F",
    "GM",
    # Consumer Staples
    "WMT",
    "PG",
    "COST",
    "KO",
    "PEP",
    "PM",
    "MO",
    "MDLZ",
    "CL",
    "TGT",
"DELL",
"DY",
    # Healthcare
    "LLY",
    "UNH",
    "JNJ",
    "ABBV",
    "MRK",
    "PFE",
    "TMO",
    "ABT",
    "DHR",
    "AMGN",
    "BMY",
    "CVS",
    "GILD",
    "ISRG",
"UNH",
"TMDX",
"TEM",
    # Financials
    "BRK-B",
    "JPM",
    "V",
    "MA",
    "BAC",
    "WFC",
    "MS",
    "GS",
    "SPGI",
    "BLK",
    "AXP",
    "C",
    "PNC",
    "USB",
    "TFC",
"SOFI",
"HOOD",
"MELI",
    # Industrials
    "GE",
    "CAT",
    "RTX",
    "UNP",
    "HON",
    "DE",
    "LMT",
    "ETN",
    "UPS",
    "BA",
    "MMM",
    "NSC",
    "CSX",
    # Energy
    "XOM",
    "CVX",
    "COP",
    "SLB",
    "EOG",
    "MPC",
    "PSX",
    "VLO",
"VST",
"CEG",
"BE",
    # Utilities & Real Estate
    "NEE",
    "SO",
    "DUK",
    "PLD",
    "AMT",
    "EQIX",
"FICO",
"ASTS",
"RKLB",

]

print(f"กำลังคำนวณ Forward PEG ด้วยอัตราเติบโตระยะยาว 3-5 ปี...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    forward_pe = info.get("forwardPE")

    # ดึงค่าอัตราการเติบโตคาดการณ์ระยะยาว (Long-term growth estimate 3-5 ปี)
    # ถ้าไม่มี จะดึงค่า pegRatio สำเร็จรูปของ Yahoo มาช่วยเทียบเคียงสัดส่วน
    growth_rate = info.get("growthEst")

    if not growth_rate and "pegRatio" in info and info["pegRatio"] and forward_pe:
      # คำนวณย้อนกลับจาก PEG สำเร็จรูปของ Yahoo หากไม่มีฟิลด์ Growth ตรงๆ
      # PEG = Forward PE / Growth -> Growth = Forward PE / PEG
      if info["pegRatio"] > 0:
        growth_rate = forward_pe / info["pegRatio"]

    # คำนวณค่า PEG ตามสูตร Peter Lynch (Forward PE หารด้วย Growth เปอร์เซ็นต์เต็ม)
    if forward_pe and growth_rate and growth_rate > 0:
      # ปรับหน่วยให้เป็นเปอร์เซ็นต์เต็ม (เช่น 0.15 กลายเป็น 15)
      g_percent = (
          growth_rate * 100 if growth_rate < 1.0 else growth_rate
      )  # ป้องกันกรณี API คืนค่าเป็นเปอร์เซ็นต์มาแล้ว
      peg = forward_pe / g_percent
    else:
      peg = None
      g_percent = None

    data.append({
        "Ticker": ticker,
        "Company": info.get("shortName", ticker),
        "Share_Price": info.get("currentPrice")
        or info.get("regularMarketPrice"),
        "Forward_PE": forward_pe,
        "3-5Y_Growth_Est_%": g_percent,
        "Forward_PEG": peg,
    })
    print(f"สำเร็จ: {ticker}")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(f"\nบันทึกข้อมูลเรียบร้อย! มีหุ้นที่คำนวณสำเร็จ {len(df)} ตัว")