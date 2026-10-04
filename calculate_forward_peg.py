import pandas as pd
import yfinance as yf

# รายชื่อหุ้นรวมกลุ่มเทคโนโลยี เซมิคอนดักเตอร์ และหุ้นยอดนิยมอื่นๆ (ไม่ให้มีชื่อซ้ำ)
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

print(f"กำลังคำนวณ Forward PEG หุ้นทั้งหมด {len(all_tickers)} ตัว...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    forward_pe = info.get("forwardPE")

    # ดึงอัตราการเติบโตคาดการณ์ (พยายามดึง growthEst หรือ earningsGrowth)
    growth_rate = info.get("growthEst")
    if not growth_rate:
      growth_rate = info.get("earningsGrowth")

    # คำนวณตามสูตร Peter Lynch: PEG = Forward P/E / Growth (%)
    if forward_pe and growth_rate and growth_rate > 0:
      # แปลงค่า growth เป็นเปอร์เซ็นต์เต็ม (เช่น 0.25 -> 25)
      g_percent = (
          growth_rate * 100 if growth_rate < 1.0 else growth_rate
      )
      peg = forward_pe / g_percent

      data.append({
          "Ticker": ticker,
          "Company": info.get("shortName", ticker),
          "Share_Price": info.get("currentPrice")
          or info.get("regularMarketPrice"),
          "Forward_PE": forward_pe,
          "3-5Y_Growth_Est_%": g_percent,
          "Forward_PEG": peg,
      })
      print(f"สำเร็จ: {ticker} (PE: {forward_pe}, Growth: {g_percent}%, PEG: {peg:.2f})")
    else:
      print(f"ข้าม {ticker}: ข้อมูลไม่ครบถ้วน")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)

# ตัดข้อมูลซ้ำ (ถ้ามี)
df = df.drop_duplicates(subset=["Ticker"])
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(f"\nบันทึกข้อมูลเรียบร้อย! คำนวณสำเร็จ {len(df)} ตัว")