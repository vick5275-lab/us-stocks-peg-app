import pandas as pd
import yfinance as yf

# รายชื่อหุ้นตัวอย่างที่ต้องการดึงข้อมูล (คุณสามารถเปลี่ยนหรือเพิ่มรายชื่อหุ้นได้ตามต้องการ)
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "INTC", "QCOM", "VST", "VRT", "AVGO", "TSM", "MA", "SNPS", "CDNS", "SOFI", "FPS", "UNH", "PLTR", "CLPT", "ORCL", "BABA", "UBER", "COST", "FN", "AXON", "ISRG", "MELI"]

data = []

print("กำลังดึงข้อมูล Forward PEG จาก Yahoo Finance...")

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # ดึงค่า Forward PE และอัตราการเติบโตคาดการณ์ (Growth Estimate)
        forward_pe = info.get("forwardPE")
        # yfinance อาจเก็บบันทึกอัตราการเติบโตในรูปแบบทศนิยม (เช่น 0.15 = 15%)
        growth_rate = info.get("earningsGrowth") or info.get("revenueGrowth") 
        
        # ถ้าไม่มีอัตราเติบโตแบบเจาะจง ให้ลองดึงจากภาพรวม
        if not growth_rate and "pegRatio" in info and info["pegRatio"]:
            # ถ้ามีค่า PEG สำเร็จรูปอยู่แล้ว สามารถใช้เทียบเคียงได้
            pass

        # กำหนดค่าสมมติหรือคำนวณหากมีข้อมูล Forward PE และ Growth
        if forward_pe and growth_rate and growth_rate > 0:
            peg = forward_pe / (growth_rate * 100)
        else:
            peg = None

        data.append({
            "Ticker": ticker,
            "Company": info.get("shortName", ticker),
            "Share_Price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "Forward_PE": forward_pe,
            "EPS_Growth_Est_%": growth_rate * 100 if growth_rate else None,
            "Forward_PEG": peg
        })
        print(f"สำเร็จ: {ticker}")
    except Exception as e:
        print(f"ข้าม {ticker} เนื่องจากเกิดข้อผิดพลาด: {e}")

# แปลงเป็น DataFrame และบันทึก
df = pd.DataFrame(data)
df.to_csv("us_stocks_final_peg.csv", index=False, encoding="utf-8-sig")
print("\nสร้างไฟล์ us_stocks_final_peg.csv สำหรับปี 2026 สำเร็จแล้ว!")