import pandas as pd
import yfinance as yf

# รายชื่อหุ้นรวมกลุ่มเซมิคอนดักเตอร์, บิ๊กเทค, การเงิน, พลังงาน, ค้าปลีก และสุขภาพ
all_tickers = [
    # Semiconductors & Chip Giants
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
"DELL",
"DY",
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
"DDOG",
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
"SOFI",
"HOOD",
"MELI",
    # Consumer Discretionary & Staples
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
    "NFLX",
    # Healthcare & Biotech
    "JNJ",
    "UNH",
    "LLY",
    "ABBV",
    "PFE",
    "MRK",
    "TMO",
    "AMGN",
"UNH",
"TMDX",
"TEM",
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
#Datacenter system
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
]

print(f"กำลังคำนวณ Forward PEG หุ้นทั้งหมด {len(all_tickers)} ตัว...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    forward_pe = info.get("forwardPE")
    growth_rate = info.get("growthEst")
    if not growth_rate:
      growth_rate = info.get("earningsGrowth")

    if forward_pe and growth_rate and growth_rate > 0:
      g_percent = growth_rate * 100 if growth_rate < 1.0 else growth_rate
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
      print(f"สำเร็จ: {ticker}")
    else:
      print(f"ข้าม {ticker}: ข้อมูลไม่ครบถ้วน")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)
df = df.drop_duplicates(subset=["Ticker"])
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(f"\nบันทึกข้อมูลเรียบร้อย! คำนวณสำเร็จ {len(df)} ตัว")