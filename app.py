import os
import pandas as pd
import streamlit as st

# 페이지 기본 설정 (컴퓨터/모바일 모두 대응하는 wide 레이아웃)
st.set_page_config(
    page_title="축제 사진 상상하고 분석하기", page_icon="📸", layout="wide"
)

# 나눔고딕 폰트 적용 및 은은한 그라데이션 배경, 스타일 커스텀 CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nanum Gothic', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    /* 카드 디자인 최적화 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: white;
        padding: 0.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 데이터 저장을 위한 폴더 및 CSV 파일 경로
UPLOAD_DIR = "uploads"
CSV_FILE = "metadata.csv"

if not os.path.exists(UPLOAD_DIR):
  os.makedirs(UPLOAD_DIR)


# 메타데이터 불러오기 함수
def load_data():
  if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if "group" not in df.columns:
      df["group"] = "1모둠"
    return df
  else:
    return pd.DataFrame(
        columns=["name", "group", "filename", "timestamp"]
    )


# 세션 상태 초기화
if "data" not in st.session_state:
  st.session_state.data = load_data()

if "is_teacher" not in st.session_state:
  st.session_state.is_teacher = False

if "zoomed_image" not in st.session_state:
  st.session_state.zoomed_image = None


# --- 상단 타이틀 및 티 안 나는 교사 진입 아이콘 ---
col_title, col_icon = st.columns([11, 1])

with col_title:
  st.title("🎉 축제 사진 상상하고 분석하기")

with col_icon:
  # 텍스트 없이 아이콘만 표시, 누르면 비밀번호 입력 팝오버
  if st.popover("👤"):
    if not st.session_state.is_teacher:
      pw_input = st.text_input(
          "비밀번호", type="password", key="teacher_pw_input"
      )
      if pw_input == "1232":
        st.session_state.is_teacher = True
        st.rerun()
      elif pw_input and pw_input != "1232":
        st.error("비밀번호 오류")
    else:
      st.success("교사 모드 활성화됨")
      if st.button("교사 모드 종료"):
        st.session_state.is_teacher = False
        st.rerun()

# 교사 모드 안내 배너
if st.session_state.is_teacher:
  st.info(
      "🔓 [교사 모드] 게시물 삭제 및 확대하여 설명하기 기능을 사용할 수"
      " 있습니다."
  )

st.divider()

# --- 사진 확대 보기 영역 (교사가 설명용으로 사용할 때) ---
if st.session_state.zoomed_image:
  st.markdown("### 🔍 확대된 사진 보기")
  with st.container(border=True):
    col_z1, col_z2 = st.columns([3, 1])
    with col_z1:
      st.image(
          st.session_state.zoomed_image,
          caption=st.session_state.get("zoomed_info", ""),
          use_container_width=True,
      )
    with col_z2:
      if st.button("❌ 확대 닫기", use_container_width=True):
        st.session_state.zoomed_image = None
        st.rerun()
  st.divider()

# --- 패들렛 스타일 1~4모둠 컬럼 레이아웃 ---
st.session_state.data = load_data()
df = st.session_state.data

groups = ["1모둠", "2모둠", "3모둠", "4모둠"]
cols = st.columns(4)

for idx, group_name in enumerate(groups):
  with cols[idx]:
    st.markdown(f"### 📌 {group_name}")

    # 모둠별 사진 추가 버튼 (+)
    with st.popover(f"➕ {group_name} 사진 올리기", use_container_width=True):
      st.markdown(f"**{group_name} 사진 등록**")
      with st.form(f"form_{group_name}", clear_on_submit=True):
        name = st.text_input("학번 / 이름", placeholder="예: 24 김동국")

        upload_type = st.radio(
            "방식 선택", ["파일 업로드", "직접 촬영"], horizontal=True
        )

        uploaded_file = None
        if upload_type == "파일 업로드":
          uploaded_file = st.file_uploader(
              "사진 선택", type=["jpg", "jpeg", "png"]
          )
        else:
          uploaded_file = st.camera_input("카메라 촬영")

        submitted = st.form_submit_button("제출하기")

        if submitted:
          if not name or not uploaded_file:
            st.warning("이름과 사진을 모두 입력/촬영해 주세요!")
          else:
            file_extension = "jpg"
            if hasattr(uploaded_file, "name"):
              file_extension = uploaded_file.name.split(".")[-1]

            safe_filename = f"{os.urandom(4).hex()}.{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)

            with open(file_path, "wb") as f:
              f.write(uploaded_file.getbuffer())

            new_row = pd.DataFrame(
                [{
                    "name": name,
                    "group": group_name,
                    "filename": safe_filename,
                    "timestamp": pd.Timestamp.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }]
            )

            st.session_state.data = pd.concat(
                [st.session_state.data, new_row], ignore_index=True
            )
            st.session_state.data.to_csv(CSV_FILE, index=False)
            st.success("등록 완료!")
            st.rerun()

    st.divider()

    # 해당 모둠의 게시물 카드 리스트 (최신순)
    group_df = df[df["group"] == group_name].iloc[::-1].reset_index(drop=True)

    if group_df.empty:
      st.caption("제출된 사진이 없습니다.")
    else:
      for i, row in group_df.iterrows():
        with st.container(border=True):
          st.markdown(f"**👤 {row['name']}**")
          file_path = os.path.join(UPLOAD_DIR, row["filename"])

          if os.path.exists(file_path):
            st.image(file_path, use_container_width=True)

            # 사진 확대 버튼 (교사 또는 학생들이 크게 볼 수 있도록)
            if st.button("🔍 크게 보기", key=f"zoom_{row['filename']}"):
              st.session_state.zoomed_image = file_path
              st.session_state.zoomed_info = (
                  f"[{row['group']}] {row['name']} 학생 제출"
              )
              st.rerun()
          else:
            st.error("이미지를 찾을 수 없습니다.")

          st.caption(f"시간: {row['timestamp']}")

          # 교사 모드일 때만 삭제 버튼 노출
          if st.session_state.is_teacher:
            if st.button("🗑️ 삭제", key=f"del_{row['filename']}"):
              if os.path.exists(file_path):
                os.remove(file_path)
              st.session_state.data = st.session_state.data[
                  st.session_state.data["filename"] != row["filename"]
              ]
              st.session_state.data.to_csv(CSV_FILE, index=False)
              st.success("삭제되었습니다.")
              st.rerun()
