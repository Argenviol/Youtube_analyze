"""
StelLive(스텔라이브) 분석 프로젝트 공통 설정.

- 채널 ID는 YouTube Data API로 직접 조회해 검증한 값입니다(핸들 추측 아님).
- API 키는 코드에 넣지 않습니다. 환경변수 YOUTUBE_API_KEY 에서 읽습니다.
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# API 키 (절대 하드코딩/커밋하지 않음)
# ---------------------------------------------------------------------------
def get_api_key() -> str:
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError(
            "환경변수 YOUTUBE_API_KEY 가 설정되어 있지 않습니다.\n"
            "  export YOUTUBE_API_KEY=발급받은_키\n"
            "후 다시 실행하세요."
        )
    return key


# ---------------------------------------------------------------------------
# 분석 대상 로스터 (2026년 기준, 공식 talents 페이지 + API 검증)
#   unit: 소속 유닛 / role: talent(탤런트) | founder(창립자)
#   창립자 강지를 포함해 총 11명 = 사용자가 말한 "멤버 11명".
#   강지는 콘텐츠 성격이 달라 별도 표기하며, INCLUDE_FOUNDER=False 로 손쉽게 제외 가능.
# ---------------------------------------------------------------------------
MEMBERS = [
    # name_ko, name_en, unit, role, channel_id, handle
    ("강지",         "Kangji",          "STELLIVE", "founder", "UCIVFv8AiQLqM9oLHTixrNYw", "gangzi1"),
    ("아야츠노 유니", "Ayatsuno Yuni",   "EVERYS",   "talent",  "UClbYIn9LDbbFZ9w2shX3K0g", "ayatsunoyuni"),
    ("사키하네 후야", "Sakihane Huya",   "EVERYS",   "talent",  "UC0YQnenKBCu5sGb7H61n6HA", "sakihanechannel"),
    ("시라유키 히나", "Shirayuki Hina",  "UNIVERSE", "talent",  "UC1afpiIuBDcjYlmruAa0HiA", "shirayukihina"),
    ("네네코 마시로", "Neneko Mashiro",  "UNIVERSE", "talent",  "UC_eeSpMBz8PG4ssdBPnP07g", "neneko_mashiro"),
    ("아카네 리제",   "Akane Lize",      "UNIVERSE", "talent",  "UC7-m6jQLinZQWIbwm9W-1iw", "akanelize"),
    ("아라하시 타비", "Arahashi Tabi",   "UNIVERSE", "talent",  "UCAHVQ44O81aehLWfy9O6Elw", "arahashitabi"),
    ("텐코 시부키",   "Tenko Shibuki",   "CLICHE",   "talent",  "UCYxLMfeX1CbMBll9MsGlzmw", "tenkoshibuki"),
    ("아오쿠모 린",   "Aokumo Rin",      "CLICHE",   "talent",  "UCQmcltnre6aG9SkDRYZqFIg", "aokumorin"),
    ("하나코 나나",   "Hanako Nana",     "CLICHE",   "talent",  "UCcA21_PzN1EhNe7xS4MJGsQ", "hanako_nana"),
    ("유즈하 리코",   "Yuzuha Riko",     "CLICHE",   "talent",  "UCj0c1jUr91dTetIQP2pFeLA", "yuzuhariko"),
]

# 그룹 공식 채널 (커버곡/MV 등) — 멤버 성과 분석에는 참고용으로만 사용
OFFICIAL_CHANNEL = ("스텔라이브 공식", "StelLive Official", "UC2b4WRE5BZ6SIUWBeJU8rwg", "stellive_official")

INCLUDE_FOUNDER = True

# 리포트·차트 등 **분석 산출물**에서 창립자(강지)를 제외한다. 수집은 전 로스터로
# 계속한다 — 특히 08 동시시청자는 소급 수집이 불가능해서, 표시에서 빼더라도 데이터는
# 계속 쌓아야 나중에 기준이 바뀌어도 복구할 수 있다. INCLUDE_FOUNDER(수집)와
# 별개의 스위치인 이유다.
EXCLUDE_FOUNDER_FROM_ANALYSIS = True


def founder_names() -> set:
    return {m[0] for m in MEMBERS if m[3] == "founder"}


def drop_founder(df, col: str = "name_ko"):
    """분석 산출물용 필터. 스위치가 꺼져 있거나 해당 컬럼이 없으면 그대로 돌려준다."""
    if not EXCLUDE_FOUNDER_FROM_ANALYSIS or col not in getattr(df, "columns", ()):
        return df
    return df[~df[col].isin(founder_names())].reset_index(drop=True)

# ---------------------------------------------------------------------------
# 데뷔일 — 모든 비교의 전제 조건
#
#   구독자·누적조회수는 "얼마나 잘했나"보다 "얼마나 오래 쌓았나"에 먼저 반응한다.
#   2019년 데뷔 채널과 2024년 데뷔 채널을 한 표에 올리면 그 표는 실력이 아니라
#   활동 기간을 재는 표가 된다. 그래서 그룹 비교는 반드시 **데뷔 시기를 맞춘 뒤**
#   한다(프로젝트 6). 여기 값이 그 기준이다.
#
#   출처: 나무위키 각 멤버 문서 / stellive.me 공지 / hololivepro.com 탤런트 페이지.
#   교차검증: YouTube 채널 개설일(publishedAt)과 ±1개월 안에서 일치하는지 확인했다.
#     예) 유니 채널 개설 2022-12-20 ↔ 데뷔 2023-01-08,
#         유니버스 3인 채널 개설 2023-06-01 ↔ 데뷔 2023-06-10~11,
#         후야 채널 개설 2025-09-16 ↔ 데뷔 2025-09-20.
#   precision="approx" 는 공식 데뷔일이 공시되지 않아 근사한 값이다. 코호트 경계
#   근처에서 이 값에 의존하는 결론은 내지 않는다.
# ---------------------------------------------------------------------------
DEBUTS = {
    # name_en: (debut_date, generation, precision)
    "Kangji":         ("2021-06-01", "창립자(0기 취급)", "approx"),
    "Ayatsuno Yuni":  ("2023-01-08", "1기 MYSTIC",      "exact"),
    "Shirayuki Hina": ("2023-06-10", "2기 UNIVERSE",    "exact"),
    "Neneko Mashiro": ("2023-06-10", "2기 UNIVERSE",    "exact"),
    "Akane Lize":     ("2023-06-11", "2기 UNIVERSE",    "exact"),
    "Arahashi Tabi":  ("2023-06-11", "2기 UNIVERSE",    "exact"),
    "Tenko Shibuki":  ("2024-05-18", "3기 CLICHE",      "exact"),
    "Aokumo Rin":     ("2024-05-18", "3기 CLICHE",      "exact"),
    "Hanako Nana":    ("2024-05-19", "3기 CLICHE",      "exact"),
    "Yuzuha Riko":    ("2024-05-19", "3기 CLICHE",      "exact"),
    "Sakihane Huya":  ("2025-09-20", "1기 EVERYS(신규)", "exact"),
}


# ---------------------------------------------------------------------------
# 경쟁사 비교(프로젝트6) 로스터 — 데뷔 코호트 매칭용
#
#   이전 버전은 홀로라이브 쪽 표본을 "유명한 사람 6명"(페코라·구라·마린 등, 2019~2020
#   데뷔)으로 골랐다. StelLive 는 2023~2025 데뷔라서, 그 비교표는 사실상
#   **4~6년 먼저 시작한 채널과 이제 막 시작한 채널을 나란히 놓은 표**였다.
#   구독자 10배 차이의 대부분은 그 시간 차이로 설명된다.
#
#   그래서 로스터를 **StelLive 각 기수와 데뷔 시기가 겹치는 기수**로 바꿨다.
#   개인의 인지도로 고르지 않고 **기수 전원**을 넣는다 — 유명한 사람만 고르면
#   그 자체가 생존편향이기 때문이다.
#
#     StelLive 1기(2023-01) ─┐
#     StelLive 2기(2023-06) ─┴─ hololive EN Advent(2023-07) · DEV_IS ReGLOSS(2023-09)
#     StelLive 3기(2024-05) ─── hololive EN Justice(2024-06) · DEV_IS FLOW GLOW(2024-11)
#     이세계아이돌(2021-12) ─── hololive JP 6기 holoX(2021-11) · ID 3기(2022-03)
#
#   이세계아이돌은 StelLive 보다 1년 반 먼저 데뷔해 StelLive 와 같은 코호트에
#   들어가지 않는다. 억지로 같은 표에 넣지 않고, 같은 시기 데뷔한 홀로라이브
#   기수와 짝지어 **"한국 2021년 코호트 vs 일본 2021년 코호트"** 로 따로 본다.
#
#   모든 channel_id 는 youtube.com/channel/<id> 응답의 og:title 로 실채널임을
#   확인했다(2026-09-18). 핸들 추측 아님.
#   후와와·모코코(FUWAMOCO)는 두 명이 채널 하나를 공유해 1행으로 넣는다.
# ---------------------------------------------------------------------------
COMPETITOR_ROSTER = [
    # group, name_ko, name_en, channel_id, debut_date, generation
    # ── 홀로라이브 JP 6기 holoX (2021-11) ────────────────────────────────
    ("홀로라이브", "라플라스 다크니스", "La+ Darknesss",  "UCENwRMx5Yh42zWpzURebzTw", "2021-11-26", "JP 6기 holoX"),
    ("홀로라이브", "타카네 루이",      "Takane Lui",      "UCs9_O1tRPMQTHQ-N_L6FU2g", "2021-11-27", "JP 6기 holoX"),
    ("홀로라이브", "하쿠이 코요리",    "Hakui Koyori",    "UC6eWCld0KwmyHFbAqK3V-Rw", "2021-11-28", "JP 6기 holoX"),
    ("홀로라이브", "사카마타 클로에",  "Sakamata Chloe",  "UCIBY1ollUsauvVi4hW4cumw", "2021-11-29", "JP 6기 holoX"),
    ("홀로라이브", "카자마 이로하",    "Kazama Iroha",    "UC_vMYWcDjmfdpH6r4TTn1MQ", "2021-11-30", "JP 6기 holoX"),
    # ── 홀로라이브 ID 3기 (2022-03) ──────────────────────────────────────
    ("홀로라이브", "벨스티아 제타",    "Vestia Zeta",     "UCTvHWSfBZgtxE4sILOaurIQ", "2022-03-25", "ID 3기"),
    ("홀로라이브", "카엘라 코발스키아", "Kaela Kovalskia", "UCZLZ8Jjx_RN2CXloOmgTHVg", "2022-03-26", "ID 3기"),
    ("홀로라이브", "코보 카나에루",    "Kobo Kanaeru",    "UCjLEmnpCNeisMxy134KPwWw", "2022-03-27", "ID 3기"),
    # ── 홀로라이브 EN Advent (2023-07) ───────────────────────────────────
    ("홀로라이브", "시오리 노벨라",    "Shiori Novella",  "UCgnfPPb9JI3e9A4cXHnWbyg", "2023-07-30", "EN Advent"),
    ("홀로라이브", "코세키 비쥬",      "Koseki Bijou",    "UC9p_lqQ0FEDz327Vgf5JwqA", "2023-07-30", "EN Advent"),
    ("홀로라이브", "네리사 레이븐크로프트", "Nerissa Ravencroft", "UC_sFNM0z0MWm9A6WlKPuMMg", "2023-07-30", "EN Advent"),
    ("홀로라이브", "후와와·모코코",    "FUWAMOCO",        "UCt9H_RpQzhxzlyBxFqrdHqA", "2023-07-30", "EN Advent"),
    # ── 홀로라이브 DEV_IS ReGLOSS (2023-09) ──────────────────────────────
    ("홀로라이브", "히오도시 아오",    "Hiodoshi Ao",     "UCMGfV7TVTmHhEErVJg1oHBQ", "2023-09-09", "DEV_IS ReGLOSS"),
    ("홀로라이브", "오토노세 카나데",  "Otonose Kanade",  "UCWQtYtq9EOB4-I5P-3fh8lA", "2023-09-09", "DEV_IS ReGLOSS"),
    ("홀로라이브", "이치죠 리리카",    "Ichijou Ririka",  "UCtyWhCj3AqKh2dXctLkDtng", "2023-09-09", "DEV_IS ReGLOSS"),
    ("홀로라이브", "쥬후테이 라덴",    "Juufuutei Raden", "UCdXAk5MpyLD8594lm_OvtGQ", "2023-09-09", "DEV_IS ReGLOSS"),
    ("홀로라이브", "토도로키 하지메",  "Todoroki Hajime", "UC1iA6_NT4mtAcIII6ygrvCw", "2023-09-09", "DEV_IS ReGLOSS"),
    # ── 홀로라이브 EN Justice (2024-06) ──────────────────────────────────
    ("홀로라이브", "엘리자베스 로즈 블러드플레임", "Elizabeth Rose Bloodflame", "UCW5uhrG1eCBYditmhL0Ykjw", "2024-06-21", "EN Justice"),
    ("홀로라이브", "기기 뮤린",        "Gigi Murin",      "UCDHABijvPBnJm7F-KlNME3w", "2024-06-21", "EN Justice"),
    ("홀로라이브", "세실리아 이머그린", "Cecilia Immergreen", "UCvN5h1ShZtc7nly3pezRayg", "2024-06-21", "EN Justice"),
    ("홀로라이브", "라오라 판테라",    "Raora Panthera",  "UCl69AEx4MdqMZH7Jtsm7Tig", "2024-06-21", "EN Justice"),
    # ── 홀로라이브 DEV_IS FLOW GLOW (2024-11) ────────────────────────────
    ("홀로라이브", "이사키 리오나",    "Isaki Riona",     "UC9LSiN9hXI55svYEBrrK-tw", "2024-11-09", "DEV_IS FLOW GLOW"),
    ("홀로라이브", "코가네이 니코",    "Koganei Niko",    "UCuI_opAVX6qbxZY-a-AxFuQ", "2024-11-09", "DEV_IS FLOW GLOW"),
    ("홀로라이브", "미즈미야 스",      "Mizumiya Su",     "UCjk2nKmHzgH5Xy-C5qYRd5A", "2024-11-09", "DEV_IS FLOW GLOW"),
    ("홀로라이브", "린도 치하야",      "Rindo Chihaya",   "UCKMWFR6lAstLa7Vbf5dH7ig", "2024-11-09", "DEV_IS FLOW GLOW"),
    ("홀로라이브", "키키라라 비비",    "Kikirara Vivi",   "UCGzTVXqMQHa4AgJVJIVvtDQ", "2024-11-09", "DEV_IS FLOW GLOW"),
    # ── 이세계아이돌 (2021-12, 전원 동시 데뷔) ───────────────────────────
    ("이세계아이돌", "아이네",  "Ine",        "UCroM00J2ahCN6k-0-oAiDxg", "2021-12-17", "1기"),
    ("이세계아이돌", "징버거",  "Jingburger", "UCHE7GBQVtdh-c1m3tjFdevQ", "2021-12-17", "1기"),
    ("이세계아이돌", "릴파",    "Lilpa",      "UC-oCJP9t47v7-DmsnmXV38Q", "2021-12-17", "1기"),
    ("이세계아이돌", "주르르",  "Jururu",     "UCTifMx1ONpElK5x6B4ng8eg", "2021-12-17", "1기"),
    ("이세계아이돌", "고세구",  "Gosegu",     "UCV9WL7sW6_KjanYkUUaIDfQ", "2021-12-17", "1기"),
    ("이세계아이돌", "비챤",    "Viichan",    "UCs6EwgxKLY9GG4QNUrP5hoQ", "2021-12-17", "1기"),
]

# 코호트 구간 — 데뷔일을 담는 서랍. 경계는 "같은 시기에 시작했다"고 부를 수 있는
# 범위(최대 ~7개월)로 잡았고, 어느 서랍에도 안 들어가는 멤버는 버리지 않고
# "코호트 없음"으로 표시한다(후야 2025-09 처럼 비교 상대가 아직 없는 경우).
# 한 코호트에 그룹이 하나뿐이면 그룹 비교는 하지 않는다 — 비교 대상이 없는데
# 표를 그리면 없는 비교를 한 것처럼 보인다.
COHORT_BINS = [
    ("2021-2022 데뷔", "2021-11-01", "2022-04-30"),
    ("2023 데뷔",      "2023-01-01", "2023-09-30"),
    ("2024 데뷔",      "2024-05-01", "2024-11-30"),
    ("2025 데뷔",      "2025-01-01", "2025-12-31"),
]


def cohort_of(debut_date: str | None) -> str | None:
    """데뷔일 -> 코호트 라벨. 어느 구간에도 없으면 None."""
    if not debut_date:
        return None
    for label, lo, hi in COHORT_BINS:
        if lo <= debut_date[:10] <= hi:
            return label
    return None


def competitor_rows():
    return [dict(group=g, name_ko=k, name_en=e, channel_id=c,
                 debut_date=d, generation=gen, cohort=cohort_of(d))
            for g, k, e, c, d, gen in COMPETITOR_ROSTER]

# 치지직(Chzzk) 채널 ID — API 검색으로 확인한 값 (name_en 기준)
CHZZK_IDS = {
    "Kangji":         "b5ed5db484d04faf4d150aedd362f34b",
    "Ayatsuno Yuni":  "45e71a76e949e16a34764deb962f9d9f",
    "Sakihane Huya":  "36ddb9bb4f17593b60f1b63cec86611d",
    "Shirayuki Hina": "b044e3a3b9259246bc92e863e7d3f3b8",
    "Neneko Mashiro": "4515b179f86b67b4981e16190817c580",
    "Akane Lize":     "4325b1d5bbc321fad3042306646e2e50",
    "Arahashi Tabi":  "a6c4ddb09cdb160478996007bff35296",
    "Tenko Shibuki":  "64d76089fba26b180d9c9e48a32600d9",
    "Aokumo Rin":     "516937b5f85cbf2249ce31b0ad046b0f",
    "Hanako Nana":    "4d812b586ff63f8a2946e64fa860bbf5",
    "Yuzuha Riko":    "8fd39bb8de623317de90654718638b10",
}


def member_rows(include_founder: bool = INCLUDE_FOUNDER):
    rows = []
    for name_ko, name_en, unit, role, cid, handle in MEMBERS:
        if role == "founder" and not include_founder:
            continue
        debut, gen, prec = DEBUTS.get(name_en, (None, None, None))
        rows.append(
            dict(name_ko=name_ko, name_en=name_en, unit=unit, role=role,
                 channel_id=cid, handle=handle,
                 debut_date=debut, generation=gen, debut_precision=prec,
                 cohort=cohort_of(debut))
        )
    return rows


def channel_ids(include_founder: bool = INCLUDE_FOUNDER):
    return [r["channel_id"] for r in member_rows(include_founder)]


# ---------------------------------------------------------------------------
# 데이터-비주얼 팔레트 — Montage(Wanted Lab Design System) 토큰 기반.
#   common/montage.py 에서 accent.foreground 세트를 그대로 가져온다.
#   멤버가 11명이고 Montage accent도 11색이라 순환 없이 1:1 매핑된다.
#
#   ⚠ 11색 카테고리는 색각 이상 사용자가 완전히 구분하기 어렵다. 색에만 의존하지
#     말고 차트에 직접 라벨을 붙이는 것을 원칙으로 한다(기존 차트도 그렇게 그린다).
# ---------------------------------------------------------------------------
from . import montage  # noqa: E402

PALETTE = {
    "series": list(montage.ACCENT_LIGHT),
    "series_dark": list(montage.ACCENT_DARK),
}

# 유닛별 대표색 (Montage accent에서 선택)
UNIT_COLORS = {
    "STELLIVE": montage.COOL_NEUTRAL[50],   # 창립자/그룹 — 중립
    "EVERYS":   montage.BLUE[45],
    "UNIVERSE": montage.RED_ORANGE[48],
    "CLICHE":   montage.GREEN[40],
}


# 멤버(영문)별 고정 색 — 어느 차트에서도 같은 멤버는 같은 색 (dataviz 원칙)
def member_colors(include_founder: bool = INCLUDE_FOUNDER):
    rows = member_rows(include_founder)
    pal = PALETTE["series"]
    return {r["name_en"]: pal[i % len(pal)] for i, r in enumerate(rows)}


INK = {
    "surface": montage.LIGHT["bg"], "surface_dark": montage.DARK["bg"],
    "text": montage.LIGHT["label"], "text_dark": montage.DARK["label"],
    "muted": montage.LIGHT["label_alt"],
    "grid": montage.LIGHT["line"], "grid_dark": montage.DARK["line"],
}
