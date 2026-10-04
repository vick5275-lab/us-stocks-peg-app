import pandas as pd
import yfinance as yf

# รายชื่อหุ้นยอดนิยมชุดใหญ่จาก S&P 500 และ Dow Jones ครอบคลุมทุก Sector
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

print(f"กำลังดึงข้อมูล Forward PEG ของหุ้นจำนวน {len(all_tickers)} ตัว...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    forward_pe = info.get("forwardPE")
    growth_rate = info.get("earningsGrowth") or info.get("revenueGrowth")

    if forward_pe and growth_rate and growth_rate > 0:
      peg = forward_pe / (growth_rate * 100)
    else:
      peg = None

    data.append({
        "Ticker": ticker,
        "Company": info.get("shortName", ticker),
        "Share_Price": info.get("currentPrice")
        or info.get("regularMarketPrice"),
        "Forward_PE": forward_pe,
        "EPS_Growth_Est_%": growth_rate * 100 if growth_rate else None,
        "Forward_PEG": peg,
    })
    print(f"สำเร็จ: {ticker}")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(
    f"\nบันทึกไฟล์สำเร็จ! มีหุ้นที่คำนวณ Forward PEG ได้ทั้งหมด {len(df)} ตัว"
)