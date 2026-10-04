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
"HOOD",
"MELI",
"FICO",
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
    "FN",
    "SOFI",
"VST",
"CEG",
"BE",
#Space
"SPCX",
"ASTS",
"RKLB",
"PL",

]

print(f"กำลังดึงข้อมูลหุ้นทั้งหมด {len(all_tickers)} ตัว...")

data = []
for ticker in all_tickers:
  try:
    stock = yf.Ticker(ticker)
    info = stock.info

    forward_pe = info.get("forwardPE")
    # ดึงค่า PEG สำเร็จรูปจาก Yahoo Finance โดยตรง (ตรงกับหน้าเว็บหลัก)
    peg = info.get("pegRatio")

    # คำนวณอัตราการเติบโตย้อนกลับมาแสดงผล: Growth = Forward P/E / PEG
    if forward_pe and peg and peg > 0:
      growth_est = forward_pe / peg
    else:
      growth_est = None

    # หากหุ้นตัวไหนไม่มีค่า PEG สำเร็จรูป แต่มี Forward PE และ Growth ให้คำนวณสำรอง
    if not peg and forward_pe:
      growth_rate = info.get("growthEst") or info.get("earningsGrowth")
      if growth_rate and growth_rate > 0:
        g_percent = (
            growth_rate * 100 if growth_rate < 1.0 else growth_rate
        )
        peg = forward_pe / g_percent
        growth_est = g_percent

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
      print(f"ข้าม {ticker}: ข้อมูล PEG ไม่สมบูรณ์")
  except Exception as e:
    print(f"ข้าม {ticker}: {e}")

df = pd.DataFrame(data)
df = df.drop_duplicates(subset=["Ticker"])
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(
    f"\nบันทึกข้อมูลเรียบร้อย! มีหุ้นที่ดึงค่า PEG สำเร็จรวมทั้งสิ้น {len(df)}"
    " ตัว"
)