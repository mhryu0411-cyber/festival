import os
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="세계 축제 이미지 분석", page_icon="🌍", layout="wide"
)

# 커스텀 CSS: expand_more 글자 숨김, 나눔고딕, 연한 파스텔 배경, 예쁜 직사각형 버튼 카드
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nanum Gothic', sans-serif !important;
    }

    /* 눈이 편안한 아주 연한 파스텔톤 배경 */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%) !important;
        background-attachment: fixed;
    }

    /* Streamlit 버그로 인한 expand_more / expand_less 아이콘 텍스트 유출 완전 차단 */
    [data-testid="stIconMaterial"], 
    span:contains("expand_more"),
    .material-symbols-outlined {
        font-size: 0px !important;
        visibility: hidden !important;
        display: none !important;
    }

    /* popover 버튼 및 상단 스타일 정돈 */
    [data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* 카드 스타일 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 1rem !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
    }

    /* 직사각형 업로드 선택 카드 스타일 */
    .choice-card-cam {
        background-color: #e0e7ff;
        border: 2px dashed #6366f1;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        color: #4338ca;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .choice-card-file {
        background-color: #f3f4f6;
        border: 2px dashed #9ca3af;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        color: #374151;
        font-weight: bold;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 데이터 저장을 위한 폴더 및 CSV 경로
UPLOAD_DIR = "uploads"
CSV_FILE = "metadata.csv"

if not os.path.exists(UPLOAD_DIR):
  os.makedirs(UPLOAD_DIR)


def load_data():
  if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if "group" not in df.columns:
      df["group"] = "1모둠"
    return df
  else:
    return pd.DataFrame(columns=["group", "filename", "timestamp"])


def save_post(group_name, file_buffer):
  file_extension = "jpg"
  if hasattr(file_buffer, "name") and "." in file_buffer.name:
    file_extension = file_buffer.name.split(".")[-1]

  safe_filename = f"{os.urandom(6).hex()}.{file_extension}"
  file_path = os.path.join(UPLOAD_DIR, safe_filename)

  with open(file_path, "wb") as f:
    f.write(file_buffer.getbuffer())

  new_row = pd.DataFrame(
      [{
          "group": group_name,
          "filename": safe_filename,
          "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
      }]
  )

  st.session_state.data = pd.concat(
      [st.session_state.data, new_row], ignore_index=True
  )
  st.session_state.data.to_csv(CSV_FILE, index=False)


# 세션 상태 초기화
if "data" not in st.session_state:
  st.session_state.data = load_data()

if "is_teacher" not in st.session_state:
  st.session_state.is_teacher = False

if "zoomed_image" not in st.session_state:
  st.session_state.zoomed_image = None

if "active_upload_group" not in st.session_state:
  st.session_state.active_upload_group = None

if "upload_mode" not in st.session_state:
  st.session_state.upload_mode = None


# --- 헤더 및 교사 비밀번호 관리 ---
col_head, col_auth = st.columns([11, 1])

with col_head:
  st.title("🌍 세계 축제 이미지 분석")
  st.caption("모둠별 학습지 공유 보드")

with col_auth:
  with st.popover("⚙️"):
    if not st.session_state.is_teacher:
      st.markdown("##### 교사 인증")
      pw_input = st.text_input(
          "비밀번호",
          type="password",
          key="teacher_pw_input",
          label_visibility="collapsed",
      )
      if pw_input == "1232":
        st.session_state.is_teacher = True
        st.success("인증 성공!")
        st.rerun()
      elif pw_input and pw_input != "1232":
        st.error("비밀번호가 다릅니다.")
    else:
      st.success("교사 모드 사용 중")
      if st.button("교사 모드 종료", use_container_width=True):
        st.session_state.is_teacher = False
        st.rerun()

if st.session_state.is_teacher:
  st.info("🔓 [교사 모드 활성화됨] 사진을 크게 보거나 삭제할 수 있습니다.")

st.divider()

# --- 사진 크게 보기 (Modal 역할) ---
if st.session_state.zoomed_image:
  with st.container(border=True):
    st.markdown("### 🔍 사진 크게 보기")
    col_img, col_close = st.columns([4, 1])
    with col_img:
      st.image(
          st.session_state.zoomed_image,
          caption=st.session_state.get("zoomed_info", ""),
          use_container_width=True,
      )
    with col_close:
      if st.button("❌ 닫기", use_container_width=True):
        st.session_state.zoomed_image = None
        st.rerun()
  st.divider()

# --- 사진 업로드 창 (선택된 모둠이 있을 때 화면 상단에 팝업처럼 노출) ---
if st.session_state.active_upload_group:
  target_group = st.session_state.active_upload_group
  with st.container(border=True):
    st.markdown(f"### 📸 {target_group} 사진 업로드")

    # [📷 카메라 촬영] / [📁 파일 선택] 직관적인 2개 정사각형/직사각형 버튼
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
      st.markdown(
          '<div class="choice-card-cam">📷 카메라 촬영</div>',
          unsafe_allow_html=True,
      )
      if st.button("카메라 열기", key="btn_cam_mode", use_container_width=True):
        st.session_state.upload_mode = "camera"

    with col_btn2:
      st.markdown(
          '<div class="choice-card-file">📁 파일 / 앨범</div>',
          unsafe_allow_html=True,
      )
      if st.button(
          "앨범에서 선택", key="btn_file_mode", use_container_width=True
      ):
        st.session_state.upload_mode = "file"

    st.write("")

    uploaded_file = None
    if st.session_state.upload_mode == "camera":
      uploaded_file = st.camera_input("카메라로 촬영하세요")
    elif st.session_state.upload_mode == "file":
      uploaded_file = st.file_uploader(
          "사진 파일 선택", type=["jpg", "jpeg", "png"]
      )

    # 사진이 들어오면 즉시 자동 업로드 완료 처리
    if uploaded_file is not None:
      save_post(target_group, uploaded_file)
      st.session_state.active_upload_group = None
      st.session_state.upload_mode = None
      st.success("성공적으로 등록되었습니다!")
      st.rerun()

    if st.button("취소", use_container_width=True):
      st.session_state.active_upload_group = None
      st.session_state.upload_mode = None
      st.rerun()

  st.divider()

# --- 패들렛 스타일 1~4모둠 보드 ---
st.session_state.data = load_data()
df = st.session_state.data

groups = ["1모둠", "2모둠", "3모둠", "4모둠"]
cols = st.columns(4)

for idx, group_name in enumerate(groups):
  with cols[idx]:
    st.markdown(f"### 📌 {group_name}")

    # 모둠별 사진 올리기 버튼
    if st.button(
        f"➕ {group_name} 사진 올리기",
        key=f"upload_btn_{group_name}",
        use_container_width=True,
    ):
      st.session_state.active_upload_group = group_name
      st.session_state.upload_mode = None
      st.rerun()

    st.write("")

    # 해당 모둠 게시물 (최신순)
    group_df = df[df["group"] == group_name].iloc[::-1].reset_index(drop=True)

    if group_df.empty:
      st.caption("제출된 사진이 없습니다.")
    else:
      for i, row in group_df.iterrows():
        with st.container(border=True):
          file_path = os.path.join(UPLOAD_DIR, row["filename"])

          if os.path.exists(file_path):
            st.image(file_path, use_container_width=True)

            if st.button("🔍 크게 보기", key=f"zoom_{row['filename']}"):
              st.session_state.zoomed_image = file_path
              st.session_state.zoomed_info = f"[{row['group']}] 제출된 사진"
              st.rerun()
          else:
            st.error("이미지를 찾을 수 없습니다.")

          st.caption(f"시간: {row['timestamp']}")

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
