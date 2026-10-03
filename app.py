import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="US Stocks Forward PEG (2026)", page_icon="📈", layout="wide"
)

st.title("📈 วิเคราะห์หุ้นเติบโตด้วยค่า Forward PEG (ปี 2026)")
st.write(
    "แสดงข้อมูลประมาณการล่วงหน้าจาก Yahoo Finance สำหรับประกอบการตัดสินใจลงทุน"
)


# โหลดข้อมูล CSV
@st.cache_data
def load_data():
  df = pd.read_csv("us_stocks_final_peg.csv")
  return df


try:
  df = load_data()

  # ตรวจสอบว่ามีข้อมูลไหม
  if df.empty:
    st.warning("ไม่พบข้อมูลในไฟล์ CSV")
  else:
    # แสดงตัวกรองแถบคอลัมน์ด้านข้าง
    st.sidebar.header("🔍 ตัวกรองข้อมูล")
    max_peg = st.sidebar.slider(
        "กรองค่า Forward PEG สูงสุดไม่เกิน:",
        0.0,
        5.0,
        2.0,
        0.1,
    )

    # กรองข้อมูลตาม PEG
    if "Forward_PEG" in df.columns:
      filtered_df = df[df["Forward_PEG"].notna() & (df["Forward_PEG"] <= max_peg)]
      filtered_df = filtered_df.sort_values("Forward_PEG")
    else:
      filtered_df = df

    # แสดงผลกราฟอันดับหุ้น Forward PEG ต่ำสุด
    st.subheader("🏆 อันดับหุ้น Forward PEG ต่ำที่สุด (น่าสนใจ)")
    if not filtered_df.empty and "Forward_PEG" in filtered_df.columns:
      chart_data = filtered_df.head(10).set_index("Ticker")[
          "Forward_PEG"
      ]
      st.bar_chart(chart_data)
    else:
      st.info("ไม่มีข้อมูลเพียงพอสำหรับแสดงกราฟ")

    # แสดงตารางข้อมูลทั้งหมด
    st.subheader("📋 ตารางข้อมูลหุ้นทั้งหมด")
    st.dataframe(filtered_df, use_container_width=True)

    # ปุ่มดาวน์โหลด
    csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลเป็น CSV",
        data=csv,
        file_name="us_stocks_forward_peg_2026.csv",
        mime="text/csv",
    )

except Exception as e:
  st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์: {e}")
  st.info(
      "กรุณาตรวจสอบว่าได้รันสคริปต์สร้างไฟล์ us_stocks_final_peg.csv เรียบร้อยแล้ว"
  )