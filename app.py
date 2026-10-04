import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="US Stocks Forward PEG (2026)", page_icon="📈", layout="wide"
)

st.title("📈 วิเคราะห์หุ้นเติบโตด้วยค่า Forward PEG (ตามหลัก Peter Lynch)")
st.write(
    "ระบบกรองและเปรียบเทียบหุ้นสหรัฐฯ ครอบคลุมหลากหลายกลุ่มอุตสาหกรรม"
)


@st.cache_data
def load_data():
  df = pd.read_csv("us_stocks_final_peg.csv")
  
  semi_tickers = [
      "NVDA", "TSM", "AVGO", "MU", "AMD", "INTC", "QCOM", "ASML",
      "ARM", "TXN", "MRVL", "ADI", "AMAT", "LRCX", "KLAC", "NXPI",
      "MCHP", "ON", "SWKS", "QRVO", "STM"
  ]
  big_tech = [
      "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NFLX", "ORCL",
      "ADBE", "CRM", "NOW", "UBER", "ABNB", "PLTR"
  ]
  financials = ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "C", "AXP", "BLK"]
  healthcare = ["JNJ", "UNH", "LLY", "ABBV", "PFE", "MRK", "TMO", "AMGN"]

  def categorize(ticker):
    if ticker in semi_tickers:
      return "Semiconductors & Chips"
    elif ticker in big_tech:
      return "Big Tech & Software"
    elif ticker in financials:
      return "Financials & Banking"
    elif ticker in healthcare:
      return "Healthcare & Biotech"
    else:
      return "Consumer, Energy & Industrials"

  df["Sector_Group"] = df["Ticker"].apply(categorize)
  return df


try:
  df = load_data()

  if df.empty:
    st.warning("ไม่พบข้อมูลในไฟล์ CSV")
  else:
    st.sidebar.header("🔍 ตัวกรองข้อมูลขั้นสูง")

    selected_sector = st.sidebar.selectbox(
        "เลือกกลุ่มอุตสาหกรรม:",
        [
            "ทั้งหมด",
            "Semiconductors & Chips",
            "Big Tech & Software",
            "Financials & Banking",
            "Healthcare & Biotech",
            "Consumer, Energy & Industrials",
"Datacenter System",
        ],
    )

    search_query = st.sidebar.text_input(
        "ค้นหาตาม Ticker หรือชื่อบริษัท:", ""
    ).upper()

    st.sidebar.subheader("📌 ช่วงค่า Forward PEG")
    min_peg, max_peg = st.sidebar.slider(
        "เลือกช่วง Forward PEG:",
        0.0,
        5.0,
        (0.0, 2.0),
        0.05,
    )

    peter_lynch_mode = st.sidebar.checkbox(
        "💡 โหมด Peter Lynch เน้นหุ้น PEG <= 1.0 เท่านั้น"
    )

    filtered_df = df.copy()

    if selected_sector != "ทั้งหมด":
      filtered_df = filtered_df[filtered_df["Sector_Group"] == selected_sector]

    if search_query:
      filtered_df = filtered_df[
          filtered_df["Ticker"].str.contains(search_query, na=False)
          | filtered_df["Company"]
          .str.upper()
          .str.contains(search_query, na=False)
      ]

    if "Forward_PEG" in filtered_df.columns:
      filtered_df = filtered_df[
          filtered_df["Forward_PEG"].notna()
          & (filtered_df["Forward_PEG"] >= min_peg)
          & (filtered_df["Forward_PEG"] <= max_peg)
      ]

      if peter_lynch_mode:
        filtered_df = filtered_df[filtered_df["Forward_PEG"] <= 1.0]

      filtered_df = filtered_df.sort_values("Forward_PEG")

    st.subheader(f"📋 รายชื่อหุ้นในกลุ่ม: {selected_sector} ({len(filtered_df)} ตัว)")
    st.dataframe(
        filtered_df.style.format(
            {
                "Share_Price": "${:.2f}",
                "Forward_PE": "{:.2f}",
                "3-5Y_Growth_Est_%": "{:.2f}%",
                "Forward_PEG": "{:.4f}",
            },
            na_rep="-",
        ),
        use_container_width=True,
    )

    csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลเป็น CSV",
        data=csv,
        file_name="us_stocks_filtered_peg.csv",
        mime="text/csv",
    )

except Exception as e:
  st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")