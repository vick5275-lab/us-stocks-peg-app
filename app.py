import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="US Stocks Forward PEG (2026)", page_icon="📈", layout="wide"
)

st.title("📈 วิเคราะห์หุ้นเติบโตด้วยค่า Forward PEG (ตามหลัก Peter Lynch)")
st.write(
    "ระบบกรองและเปรียบเทียบหุ้นสหรัฐฯ พร้อมจำแนกตามกลุ่มอุตสาหกรรม"
)


# โหลดข้อมูล CSV
@st.cache_data
def load_data():
  df = pd.read_csv("us_stocks_final_peg.csv")
  # กำหนดกลุ่มอุตสาหกรรมคร่าวๆ เพื่อให้วิเคราะห์ง่ายขึ้น
  semi_tickers = [
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
  ]
  big_tech = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NFLX", "ORCL"]

  def categorize(ticker):
    if ticker in semi_tickers:
      return "Semiconductors & Chips"
    elif ticker in big_tech:
      return "Big Tech & Software"
    else:
      return "Other Sectors (Financial, Consumer, Health)"

  df["Sector_Group"] = df["Ticker"].apply(categorize)
  return df


try:
  df = load_data()

  if df.empty:
    st.warning("ไม่พบข้อมูลในไฟล์ CSV")
  else:
    st.sidebar.header("🔍 ตัวกรองข้อมูลขั้นสูง")

    # ตัวกรองเลือกกลุ่มอุตสาหกรรม
    selected_sector = st.sidebar.selectbox(
        "เลือกกลุ่มอุตสาหกรรม:",
        ["ทั้งหมด", "Semiconductors & Chips", "Big Tech & Software", "Other Sectors (Financial, Consumer, Health)"]
    )

    # ช่องค้นหา Ticker หรือชื่อบริษัท
    search_query = st.sidebar.text_input(
        "ค้นหาตาม Ticker หรือชื่อบริษัท:", ""
    ).upper()

    # ตัวกรองช่วง Forward PEG
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

    # กรองตามกลุ่มอุตสาหกรรม
    if selected_sector != "ทั้งหมด":
      filtered_df = filtered_df[filtered_df["Sector_Group"] == selected_sector]

    # กรองด้วยช่องค้นหา
    if search_query:
      filtered_df = filtered_df[
          filtered_df["Ticker"].str.contains(search_query, na=False)
          | filtered_df["Company"]
          .str.upper()
          .str.contains(search_query, na=False)
      ]

    # กรองด้วยช่วง Forward PEG
    if "Forward_PEG" in filtered_df.columns:
      filtered_df = filtered_df[
          filtered_df["Forward_PEG"].notna()
          & (filtered_df["Forward_PEG"] >= min_peg)
          & (filtered_df["Forward_PEG"] <= max_peg)
      ]

      if peter_lynch_mode:
        filtered_df = filtered_df[filtered_df["Forward_PEG"] <= 1.0]

      filtered_df = filtered_df.sort_values("Forward_PEG")

    # แสดงผล
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

    # ปุ่มดาวน์โหลด
    csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลเป็น CSV",
        data=csv,
        file_name="us_stocks_filtered_peg.csv",
        mime="text/csv",
    )

except Exception as e:
  st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")