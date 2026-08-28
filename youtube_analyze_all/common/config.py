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
# 경쟁사 비교(프로젝트6)용 로스터 — 모두 YouTube API로 검증한 채널 ID
# ---------------------------------------------------------------------------
COMPETITORS = {
    "홀로라이브": [
        # name_ko, name_en, channel_id
        ("우사다 페코라", "Usada Pekora", "UC1DCedRgGHBdm81E1llLhOQ"),
        ("가우르 구라", "Gawr Gura", "UCoSrY_IQQVpmIRZ9Xf-y93g"),
        ("호쇼 마린", "Houshou Marine", "UCCzUftO8KOVkV4wQG1vkUvg"),
        ("모리 캘리오프", "Mori Calliope", "UCL_qhgtOy0dy1Agp8vkySQg"),
        ("모모스즈 네네", "Momosuzu Nene", "UCAWSyEs_Io8MtpY3m-zqILA"),
        ("이누가미 코로네", "Inugami Korone", "UChAnqc_AY5_I3Px5dig3X1Q"),
    ],
    "이세계아이돌": [
        ("아이네", "Ine", "UCroM00J2ahCN6k-0-oAiDxg"),
        ("징버거", "Jingburger", "UCHE7GBQVtdh-c1m3tjFdevQ"),
        ("릴파", "Lilpa", "UC-oCJP9t47v7-DmsnmXV38Q"),
        ("주르르", "Jururu", "UCTifMx1ONpElK5x6B4ng8eg"),
        ("고세구", "Gosegu", "UCV9WL7sW6_KjanYkUUaIDfQ"),
        ("비챤", "Viichan", "UCs6EwgxKLY9GG4QNUrP5hoQ"),
    ],
}

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
        rows.append(
            dict(name_ko=name_ko, name_en=name_en, unit=unit, role=role,
                 channel_id=cid, handle=handle)
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
