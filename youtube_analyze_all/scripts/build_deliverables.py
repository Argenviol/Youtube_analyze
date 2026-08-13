"""
저장소 루트에 `결과물/` 을 생성한다.

각 프로젝트 폴더에는 코드(collect/analyze/build_site)·원천 데이터·SQLite 가 함께 들어
있어서, 결과만 보고 싶은 사람에게는 뒤져야 할 것이 너무 많다. `결과물/` 은 **읽을 것만**
모아둔다 — 리포트·차트·대시보드.

  python scripts/build_deliverables.py

`결과물/` 은 전량 생성물이다. 직접 고치지 말 것 — 다음 실행에서 덮어쓴다.
원본을 고치고 이 스크립트를 다시 돌리면 된다. refresh.py 가 분석 후 자동으로 호출하므로
평소에는 따로 실행할 일이 없다.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "결과물"

# 제목과 한 줄 요약은 여기서 관리한다. REPORT.md 의 '핵심 요약' 형식이 프로젝트마다
# 달라서(09는 '무엇을 찾지 못했는가', 11은 레이어 구조) 자동 추출이 안정적이지 않다.
PROJECTS = [
    ("01_member_channel_performance", "멤버별 유튜브 채널 성과",
     "구독자 규모와 도달 효율은 반대로 간다 — 참여율↔구독자 상관 -0.72"),
    ("02_cover_song_ranking", "커버곡 성과 랭킹",
     "커버 362곡 집계 · 총 조회수 1위 아카네 리제 102.4M(40곡)"),
    ("03_chzzk_stream_pattern", "치지직 방송 패턴",
     "다시보기 3,243건 · 방송이 가장 많이 시작되는 시간대는 새벽 1시(KST)"),
    ("04_kirinuki_ecosystem", "키리누키(2차창작) 생태계",
     "팬 클립 257개·팬채널 66개 · 생태계 표본 합계 조회수 20.4M"),
    ("05_comment_sentiment", "댓글 여론/감성",
     "상위 댓글 330개 직접 분류 · 긍정 80% · 최다 토픽은 성격·개그"),
    ("06_competitor_comparison", "경쟁사 비교",
     "StelLive 도달 효율 57% — 홀로라이브 13%, 이세돌 23%보다 높다"),
    ("07_market_analysis", "버추얼 크리에이터 시장",
     "VTuber 시장 2026년 약 31.3억 달러 · 치지직 MAU 242만(YoY +17%)"),
    ("08_live_viewership", "동시시청자 시계열",
     "소급 불가능한 유일한 지표 — 10분 간격 자체 수집으로만 얻어진다"),
    ("09_dart_financials", "DART 재무 분석",
     "핵심 발견은 부재 — 스텔라이브 운영법인이 DART 기업코드 마스터에 없다"),
    ("10_hoyoverse", "호요버스 캐릭터 인기도",
     "회사가 미는 캐릭터(길가메시)와 유저가 반응하는 캐릭터(반디)는 다르다"),
    ("11_fan_commerce", "팬 커머스",
     "팬딩 크리에이터 111명·67티어 · 멤버십 가격대 1,000원~550,000원"),
]


def _copy_project(slug: str) -> dict:
    """리포트·차트·대시보드만 골라 복사하고 무엇을 담았는지 돌려준다."""
    src, dst = ROOT / slug, OUT / slug
    dst.mkdir(parents=True, exist_ok=True)

    report = src / "REPORT.md"
    if report.exists():
        shutil.copy2(report, dst / "REPORT.md")

    charts = sorted((src / "charts").glob("*.png"))
    if charts:
        (dst / "charts").mkdir(exist_ok=True)
        for png in charts:
            shutil.copy2(png, dst / "charts" / png.name)

    index = src / "site" / "index.html"
    if index.exists():
        shutil.copy2(index, dst / "index.html")

    return {"charts": len(charts), "report": report.exists(), "site": index.exists()}


def _index_md(rows: list[tuple[str, str, str, dict]]) -> str:
    lines = [
        "# 결과물",
        "",
        "StelLive 데이터 분석 포트폴리오 **11개 프로젝트의 결과물만** 모았습니다.",
        "코드·원천 데이터·SQLite 는 각 프로젝트 폴더(`youtube_analyze_all/`)에 그대로 있고,",
        "여기에는 읽을 것만 있습니다 — 리포트(`REPORT.md`)·차트(`charts/`)·대시보드(`index.html`).",
        "",
        "## 프로젝트",
        "",
        "| # | 프로젝트 | 핵심 발견 | 리포트 | 차트 | 대시보드 |",
        "|---|----------|-----------|--------|------|----------|",
    ]
    for i, (slug, title, headline, got) in enumerate(rows, 1):
        report = f"[REPORT.md]({slug}/REPORT.md)" if got["report"] else "—"
        charts = f"[{got['charts']}종]({slug}/charts/)" if got["charts"] else "—"
        site = f"[index.html]({slug}/index.html)" if got["site"] else "—"
        lines.append(f"| {i} | {title} | {headline} | {report} | {charts} | {site} |")

    total_charts = sum(r[3]["charts"] for r in rows)
    lines += [
        "",
        f"프로젝트 11개 · 리포트 {sum(1 for r in rows if r[3]['report'])}건 · "
        f"차트 {total_charts}종 · 대시보드 {sum(1 for r in rows if r[3]['site'])}건.",
        "",
        "## 대시보드 여는 법",
        "",
        "`index.html` 은 CSS·데이터를 안에 품은 자체완결 파일이라 그냥 브라우저로 열면 됩니다",
        "(GitHub 웹에서는 HTML 이 렌더링되지 않으니 내려받아서 열어야 합니다).",
        "",
        "> 이 폴더는 `youtube_analyze_all/scripts/build_deliverables.py` 가 생성합니다.",
        "> 직접 고치면 다음 실행에서 덮어써집니다 — 원본을 고치고 스크립트를 다시 도세요.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    # 프로젝트가 지워졌다 남은 잔재를 끌고 가지 않도록 통째로 다시 만든다.
    if OUT.exists():
        shutil.rmtree(OUT)

    rows = []
    for slug, title, headline in PROJECTS:
        if not (ROOT / slug).is_dir():
            print(f"  ! {slug} 없음 — 건너뜀")
            continue
        got = _copy_project(slug)
        rows.append((slug, title, headline, got))
        print(f"  ✓ {slug}  차트 {got['charts']}종")

    (OUT / "README.md").write_text(_index_md(rows), encoding="utf-8")
    print(f"\n결과물 -> {OUT}  (프로젝트 {len(rows)}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
