import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="US Stocks PEG Screener",
    page_icon="📈",
    layout="wide"
)

st.title("📈 US Stocks PEG Ratio Screener & Ranking")
st.markdown("ตารางและกราฟวิเคราะห์ค่า PEG ของหุ้นสหรัฐ")


@st.cache_data
def load_data():
  if not os.path.exists("us_stocks_final_peg.csv"):
    return None
  df = pd.read_csv("us_stocks_final_peg.csv")
  return df


df = load_data()

if df is None or df.empty:
  st.error(
      "ไม่พบไฟล์ `us_stocks_final_peg.csv` กรุณารันสคริปต์คำนวณ PEG ก่อน"
  )
else:
  st.sidebar.header("ตัวกรองข้อมูล (Filters)")
  search_ticker = st.sidebar.text_input(
      "ค้นหาหุ้น (Ticker)", ""
  ).upper()
  only_valid_peg = st.sidebar.checkbox(
      "แสดงเฉพาะหุ้นที่มีค่า PEG เท่านั้น", value=True
  )
  max_peg_slider = st.sidebar.slider(
      "PEG สูงสุด",
      min_value=0.0,
      max_value=10.0,
      value=3.0,
      step=0.1
  )

  filtered_df = df.copy()

  if only_valid_peg:
    filtered_df = filtered_df.dropna(subset=["PEG"])

  filtered_df = filtered_df[filtered_df["PEG"] <= max_peg_slider]

  if search_ticker:
    filtered_df = filtered_df[
        filtered_df["Ticker"].str.contains(search_ticker, na=False)
    ]

  # แสดงสถิติ
  col1, col2, col3 = st.columns(3)
  col1.metric("จำนวนหุ้นทั้งหมด", len(df))
  col2.metric("หุ้นหลังกรอง", len(filtered_df))
  valid_avg_peg = (
      filtered_df["PEG"].mean() if not filtered_df["PEG"].empty else 0
  )
  col3.metric("PEG เฉลี่ย", f"{valid_avg_peg:.2f}")

  st.markdown("---")

  # --- ส่วนกราฟจัดอันดับหุ้น PEG ต่ำสุด ---
  st.subheader("📊 จัดอันดับหุ้น PEG ต่ำที่สุด (Top Lowest PEG)")
  chart_data = (
      filtered_df.dropna(subset=["PEG"])
      .sort_values("PEG")
      .head(15)
  )

  if not chart_data.empty:
    chart_df = chart_data.set_index("Ticker")["PEG"]
    st.bar_chart(chart_df)
  else:
    st.info("ไม่มีข้อมูลเพียงพอสำหรับแสดงกราฟ")

  st.markdown("---")

  # ตารางข้อมูล
  st.subheader("📋 ตารางข้อมูลหุ้นทั้งหมด")
  display_df = filtered_df.rename(
      columns={
          "Ticker": "สัญลักษณ์ (Ticker)",
          "Report Date": "วันที่รายงานงบ",
          "Fiscal Year": "ปีบัญชี",
          "Diluted EPS": "EPS",
          "Previous EPS": "EPS ปีก่อน",
          "EPS Growth for PEG %": "EPS Growth (%)",
          "PE_Ratio": "P/E Ratio",
          "PEG": "PEG Ratio",
      }
  )

  st.dataframe(
      display_df.style.format(
          {
              "EPS": "{:.2f}",
              "EPS ปีก่อน": "{:.2f}",
              "EPS Growth (%)": "{:.2f}%",
              "P/E Ratio": "{:.2f}",
              "PEG Ratio": "{:.2f}",
          }
      ),
      use_container_width=True,
      height=400,
  )

  csv_data = display_df.to_csv(index=False).encode("utf-8-sig")
  st.download_button(
      label="📥 ดาวน์โหลดข้อมูล CSV",
      data=csv_data,
      file_name="filtered_us_stocks_peg.csv",
      mime="text/csv",
  )