import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="US Stocks Forward PEG (2026)", page_icon="📈", layout="wide"
)

st.title("📈 วิเคราะห์หุ้นเติบโตด้วยค่า Forward PEG (ปี 2026)")
st.write(
    "แสดงข้อมูลประมาณการล่วงหน้าจาก Yahoo Finance สำหรับประกอบการตัดสินใจลงทุน"
)


@st.cache_data
def load_data():
  return pd.read_csv("us_stocks_final_peg.csv")


try:
  df = load_data()

  if df.empty:
    st.warning("ไม่พบข้อมูลในไฟล์ CSV")
  else:
    st.sidebar.header("🔍 ตัวกรองข้อมูล")

    # เพิ่มช่องค้นหา Ticker หรือชื่อบริษัท
    search_query = st.sidebar.text_input(
        "ค้นหาตาม Ticker หรือชื่อบริษัท:", ""
    ).upper()

    max_peg = st.sidebar.slider(
        "กรองค่า Forward PEG สูงสุดไม่เกิน:", 0.0, 5.0, 2.0, 0.1
    )

    filtered_df = df.copy()

    # กรองด้วยช่องค้นหา
    if search_query:
      filtered_df = filtered_df[
          filtered_df["Ticker"].str.contains(search_query, na=False)
          | filtered_df["Company"]
          .str.upper()
          .str.contains(search_query, na=False)
      ]

    # กรองด้วยค่า PEG
    if "Forward_PEG" in filtered_df.columns:
      filtered_df = filtered_df[
          filtered_df["Forward_PEG"].notna()
          & (filtered_df["Forward_PEG"] <= max_peg)
      ]
      filtered_df = filtered_df.sort_values("Forward_PEG")

    st.subheader("🏆 อันดับหุ้น Forward PEG ต่ำที่สุด (น่าสนใจ)")
    if not filtered_df.empty and "Forward_PEG" in filtered_df.columns:
      chart_data = filtered_df.head(10).set_index("Ticker")[
          "Forward_PEG"
      ]
      st.bar_chart(chart_data)
    else:
      st.info("ไม่พบข้อมูลตามเงื่อนไขที่ค้นหา")

    st.subheader("📋 ตารางข้อมูลหุ้นทั้งหมด")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลเป็น CSV",
        data=csv,
        file_name="us_stocks_forward_peg_2026.csv",
        mime="text/csv",
    )

except Exception as e:
  st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")