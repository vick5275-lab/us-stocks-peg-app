import pandas as pd
import requests
import yfinance as yf

print("กำลังดึงรายชื่อหุ้นกลุ่ม S&P 500 และ Dow Jones...")

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# 1. ดึง S&P 500
try:
  url_sp500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
  response = requests.get(url_sp500, headers=headers)
  sp500_df = pd.read_html(response.text)[0]
  sp500_tickers = sp500_df["Symbol"].tolist()
except Exception as e:
  print(f"ดึง S&P 500 ไม่สำเร็จ: {e}")
  sp500_tickers = []

# 2. ดึง Dow Jones
try:
  url_dow = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
  response = requests.get(url_dow, headers=headers)
  dow_df = pd.read_html(response.text)[1]
  dow_tickers = dow_df["Symbol"].tolist()
except Exception as e:
  print(f"ดึง Dow Jones ไม่สำเร็จ: {e}")
  dow_tickers = []

# รวมรายชื่อและแก้สัญลักษณ์จุดให้ตรงกับ yfinance (เช่น BRK.B เป็น BRK-B)
all_tickers = sorted(
    list(
        set(
            [str(t).replace(".", "-") for t in sp500_tickers + dow_tickers]
            if sp500_tickers or dow_tickers
            else [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "NVDA",
                "META",
                "TSLA",
                "JPM",
                "V",
                "JNJ",
                "WMT",
                "PG",
            ]
        )
    )
)

print(
    f"พบรายชื่อหุ้นทั้งหมด {len(all_tickers)} ตัว กำลังดึงข้อมูล Forward"
    " PEG..."
)

data = []
for idx, ticker in enumerate(all_tickers):
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
  except Exception:
    pass

df = pd.DataFrame(data)
df = df.dropna(subset=["Forward_PEG"])
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")

print(
    f"\nบันทึกข้อมูลสำเร็จ! มีหุ้นที่คำนวณ Forward PEG ได้ทั้งหมด {len(df)} ตัว"
)