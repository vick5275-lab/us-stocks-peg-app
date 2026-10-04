import pandas as pd
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="US Stocks Forward PEG (2026)", page_icon="📈", layout="wide"
)

st.title("📈 วิเคราะห์หุ้นเติบโตด้วยค่า Forward PEG (ตามหลัก Peter Lynch)")
st.write(
    "ระบบกรองและวิเคราะห์หุ้นสหรัฐฯ ด้วย Forward P/E และอัตราการเติบโตระยะยาว"
)


# โหลดข้อมูล CSV
@st.cache_data
def load_data():
  return pd.read_csv("us_stocks_final_peg.csv")


try:
  df = load_data()

  if df.empty:
    st.warning("ไม่พบข้อมูลในไฟล์ CSV")
  else:
    st.sidebar.header("🔍 ตัวกรองข้อมูลขั้นสูง")

    # ช่องค้นหา Ticker หรือชื่อบริษัท
    search_query = st.sidebar.text_input(
        "ค้นหาตาม Ticker หรือชื่อบริษัท:", ""
    ).upper()

    # ปรับปรุงตัวกรอง PEG ให้เลือกช่วงได้ (Min - Max)
    st.sidebar.subheader("📌 ช่วงค่า Forward PEG")
    min_peg, max_peg = st.sidebar.slider(
        "เลือกช่วง Forward PEG ที่ต้องการ:",
        0.0,
        5.0,
        (0.0, 1.5),  # ค่าเริ่มต้นกำหนดให้กรองหุ้น PEG ไม่เกิน 1.5 (Undervalued)
        0.05,
    )

    # ปุ่มลัดเลือกสไตล์ Peter Lynch (PEG <= 1.0 ถือว่าน่าสนใจมาก)
    peter_lynch_mode = st.sidebar.checkbox(
        "💡 โหมด Peter Lynch เน้นหุ้น PEG <= 1.0 เท่านั้น"
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

    # แสดงกราฟหุ้น Forward PEG ต่ำที่สุด 10 อันดับแรก
    st.subheader(
        f"🏆 อันดับหุ้น Forward PEG ต่ำที่สุด (ช่วง {min_peg} - {max_peg})"
    )
    if not filtered_df.empty and "Forward_PEG" in filtered_df.columns:
      chart_data = (
          filtered_df.head(10).set_index("Ticker")["Forward_PEG"].dropna()
      )
      if not chart_data.empty:
        st.bar_chart(chart_data)
      else:
        st.info("ไม่มีข้อมูลกราฟในช่วงที่เลือก")
    else:
      st.info("ไม่พบหุ้นที่ตรงกับเงื่อนไขตัวกรองนี้ ลองขยายช่วง PEG ดูครับ")

    # แสดงตารางข้อมูลทั้งหมด
    st.subheader(f"📋 รายชื่อหุ้นเข้าเกณฑ์ ({len(filtered_df)} ตัว)")
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