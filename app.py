import os
import pandas as pd
import streamlit as st

# 페이지 기본 설정 (모바일 최적화 레이아웃)
st.set_page_config(
    page_title="축제 사진 상상하고 분석하기", page_icon="📸", layout="centered"
)

# 은은한 그라데이션 배경 및 모바일 최적화 CSS 적용
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    /* 카드 디자인 최적화 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: white;
        padding: 1rem;
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
        columns=[
            "name",
            "group",
            "filename",
            "caption",
            "analysis",
            "timestamp",
        ]
    )


# 세션 상태 초기화
if "data" not in st.session_state:
  st.session_state.data = load_data()

if "is_teacher" not in st.session_state:
  st.session_state.is_teacher = False

# --- 상단 타이틀 및 티 안 나는 교사 진입 (사람 모양 아이콘) ---
col_title, col_icon = st.columns([6, 1])

with col_title:
  st.title("🎉 축제 사진 상상하고 분석하기")

with col_icon:
  # 티 안 나는 사람 모양 아이콘 버튼
  if st.popover("👤", help=""):
    st.markdown("### 🔒 교사 인증")
    pw_input = st.text_input(
        "비밀번호를 입력하세요", type="password", key="teacher_pw_input"
    )
    if pw_input == "1232":
      st.session_state.is_teacher = True
      st.success("교사 모드 활성화됨!")
      st.rerun()
    elif pw_input and pw_input != "1232":
      st.error("비밀번호가 틀렸습니다.")

# 교사 모드 활성화 상태 표시
if st.session_state.is_teacher:
  st.info("🔓 [교사 모드 활성화됨] 하단에서 게시물을 삭제할 수 있습니다.")
  if st.button("교사 모드 종료하기"):
    st.session_state.is_teacher = False
    st.rerun()

st.markdown(
    "축제 속 순간을 포착한 사진을 올리고, 그에 담긴 의미를 상상하고 분석해"
    " 보세요!"
)
st.divider()

# --- 메뉴 선택 (학생 제출용 vs 모둠별 갤러리) ---
menu = st.radio(
    "메뉴 선택", ["📸 사진 제출하기", "👀 모둠별 갤러리 보기"], horizontal=True
)

# 1. 학생 제출용 화면
if menu == "📸 사진 제출하기":
  st.subheader("📝 사진 및 분석 내용 제출")

  with st.form("submission_form", clear_on_submit=True):
    name = st.text_input("학번 / 이름", placeholder="예: 24학번 김동국")
    group = st.selectbox(
        "소속 모둠 선택", ["1모둠", "2모둠", "3모둠", "4모둠"]
    )
    uploaded_file = st.file_uploader(
        "축제 사진 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"]
    )
    caption = st.text_input(
        "사진 제목 (한 줄 요약)", placeholder="예: 축제 주무대의 뜨거운 열기"
    )
    analysis = st.text_area(
        "상상 및 분석 내용",
        placeholder=(
            "이 사진 속 상황을 공간적/사회적 맥락에서 자유롭게 분석해 주세요."
        ),
    )

    submitted = st.form_submit_button("제출하기")

    if submitted:
      if not name or not uploaded_file or not caption or not analysis:
        st.warning("모든 항목을 빠짐없이 입력하고 사진을 첨부해 주세요!")
      else:
        # 파일 저장
        file_extension = uploaded_file.name.split(".")[-1]
        safe_filename = f"{os.urandom(4).hex()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as f:
          f.write(uploaded_file.getbuffer())

        # 데이터 추가 후 저장
        new_row = pd.DataFrame(
            [{
                "name": name,
                "group": group,
                "filename": safe_filename,
                "caption": caption,
                "analysis": analysis,
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            }]
        )

        st.session_state.data = pd.concat(
            [st.session_state.data, new_row], ignore_index=True
        )
        st.session_state.data.to_csv(CSV_FILE, index=False)

        st.success(
            "성공적으로 제출되었습니다! 모둠별 갤러리에서 확인할 수 있습니다."
        )

# 2. 모둠별 갤러리 보기 (패들렛 스타일 1~4모둠 탭)
else:
  st.subheader("👀 모둠별 갤러리")

  # 최신 데이터 동기화
  st.session_state.data = load_data()
  df = st.session_state.data

  # 1~4모둠 탭 구성 (옆으로 넘기는 형태)
  tabs = st.tabs(["1모둠", "2모둠", "3모둠", "4모둠"])
  groups = ["1모둠", "2모둠", "3모둠", "4모둠"]

  for idx, tab in enumerate(tabs):
    with tab:
      target_group = groups[idx]
      group_df = df[df["group"] == target_group]

      if group_df.empty:
        st.info(f"{target_group}에 제출된 게시물이 없습니다.")
      else:
        # 최신순 정렬
        group_df_sorted = group_df.iloc[::-1].reset_index(drop=True)

        for i, row in group_df_sorted.iterrows():
          with st.container(border=True):
            st.markdown(f"**👤 {row['name']}**")
            file_path = os.path.join(UPLOAD_DIR, row["filename"])

            if os.path.exists(file_path):
              st.image(file_path, use_container_width=True)
            else:
              st.error("이미지 파일을 찾을 수 없습니다.")

            st.markdown(f"### 📌 {row['caption']}")
            st.info(row["analysis"])
            st.caption(f"제출 시간: {row['timestamp']}")

            # 교사 모드일 때만 삭제 버튼 표시
            if st.session_state.is_teacher:
              if st.button(
                  f"🗑️ 이 게시물 삭제 ({row['name']})", key=f"del_{row['filename']}"
              ):
                if os.path.exists(file_path):
                  os.remove(file_path)
                st.session_state.data = st.session_state.data[
                    st.session_state.data["filename"] != row["filename"]
                ]
                st.session_state.data.to_csv(CSV_FILE, index=False)
                st.success("게시물이 삭제되었습니다.")
                st.rerun()
