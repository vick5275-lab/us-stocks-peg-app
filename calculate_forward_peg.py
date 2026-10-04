import pandas as pd
import yfinance as yf

# รายชื่อหุ้นรวมกลุ่มเทคโนโลยี เซมิคอนดักเตอร์ และหุ้นยอดนิยมอื่นๆ
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

print(f"กำลังดึงค่า Forward PE และ PEG Ratio ของหุ้น {len(all_tickers)} ตัว...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    forward_pe = info.get("forwardPE")
    # ดึงค่า PEG สำเร็จรูปจาก Yahoo Finance โดยตรง (ซึ่งคำนวณจากประมาณการระยะยาวแล้ว)
    peg = info.get("pegRatio")

    # คำนวณอัตราการเติบโตย้อนกลับ (Growth) เพื่อแสดงผลในตาราง: Growth = Forward P/E / PEG
    if forward_pe and peg and peg > 0:
      growth_est = forward_pe / peg
    else:
      growth_est = None

    if forward_pe and peg and peg > 0:
      data.append({
          "Ticker": ticker,
          "Company": info.get("shortName", ticker),
          "Share_Price": info.get("currentPrice")
          or info.get("regularMarketPrice"),
          "Forward_PE": forward_pe,
          "3-5Y_Growth_Est_%": growth_est,
          "Forward_PEG": peg,
      })
      print(f"สำเร็จ: {ticker} (PEG: {peg})")
    else:
      print(f"ข้าม {ticker}: ไม่มีข้อมูล PEG ที่สมบูรณ์")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(
    f"\nบันทึกข้อมูลเรียบร้อย! มีหุ้นที่ดึงค่า PEG สำเร็จรูปสำเร็จ {len(df)} ตัว"
)