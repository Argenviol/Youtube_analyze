"""
프로젝트11 · 수집 단계
"팬덤은 얼마를 쓰고, 그 돈은 회사에 남는가?" — 3개 레이어를 수집한다.

  python 11_fan_commerce/collect.py

레이어 1. 가격 구조 — 팬딩(Fanding)의 VTuber 카테고리 크리에이터 멤버십 티어 가격.
  공개 REST 엔드포인트(`/rest/explorer/creator_list`)로 크리에이터 목록을 받고,
  각 크리에이터의 공개 멤버십 페이지(`/en/@{url}/membership`, 로그인 불필요)에서
  가격을 읽는다. robots.txt(`https://fanding.kr/robots.txt`)는 `/studio/*`,
  `/app-map`, `/account-info` 등 관리자·결제 영역만 막고 있고, 이 두 경로는
  포함되지 않는다 — 확인 후 수집.

레이어 2. 실제 지출 — 텀블벅(Tumblbug) VTuber 관련 크라우드펀딩 프로젝트.
  ⚠ 텀블벅은 이 레이어를 **자동 수집할 수 없다.** robots.txt
  (`https://tumblbug.com/robots.txt`)가 `Disallow: /api/`를 명시하는데, 실제로
  모금액·후원자 수·달성률 등 모든 수치는 `tumblbug.com/api/v2`·`v3` 엔드포인트에서만
  온다(프로젝트 상세 페이지 HTML 자체는 클라이언트 렌더링 껍데기라 값이 없다 —
  React 앱이 뜬 뒤 `/api/v3/project/{slug}/detail`을 호출해야 채워진다). 이 스크립트는
  `requests`만 쓰고 JS를 실행하지 않으므로애초에 그 값에 접근하지 못하고, 설령
  헤드리스 브라우저로 우회하더라도 매 실행마다 동일한 `/api/` 엔드포인트를 반복
  호출하는 셈이라 robots.txt 취지를 어기게 된다.
  대안으로 **이미 공개된 결과**(텀블벅 자사 발표·언론 보도, 그리고 프로젝트 상세
  페이지를 1회성으로 직접 열람해 확인한 수치)를 출처와 함께 정적 데이터셋으로
  기록한다 — `CROWDFUNDING_PROJECTS` 참고. 재실행해도 이 레이어는 갱신되지
  않는다(정직하게 `source_type`에 표기).
  와디즈(Wadiz)는 robots.txt는 우호적이지만(개별 캠페인 페이지 차단 없음) 검색
  결과상 VTuber 카테고리 캠페인 자체가 사실상 없어(국내 버튜버 크라우드펀딩은
  텀블벅에 쏠려 있다) 이 프로젝트에서는 다루지 않는다 — README 참고.

레이어 3. 회사에 남는 것 — 09_dart_financials가 이미 확보한 감사보고서 재무제표를
  읽기 전용으로 재사용한다(패러블엔터테인먼트·샌드박스네트워크). DART 재수집 없음.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ROOT = HERE.parent
PROJECT09_METRICS = ROOT / "09_dart_financials" / "data" / "company_metrics.csv"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# ---------------------------------------------------------------------------
# 레이어 1 · 팬딩(Fanding) VTuber 카테고리 멤버십 가격
# ---------------------------------------------------------------------------
FANDING_BASE = "https://fanding.kr"
FANDING_VTUBER_CATEGORY_NO = 57  # /en/explorer/category/7 페이지가 내부적으로 쓰는 값(확인됨)

# Nuxt가 window.__NUXT__ 를 "공유값은 문자 변수로 치환"하는 devalue 방식 직렬화로
# 내보내기 때문에 전체를 JSON으로 파싱할 수 없다(예: renewable:a — a는 다른 곳의 공유값).
# 하지만 title(고유 문자열)과 price(고유 정수)는 절대 공유·치환되지 않는다는 걸
# 여러 크리에이터 페이지에서 직접 확인했다 — title 다음에 operationType, renewable을
# 거쳐 price가 바로 이어지는 순서도 고정돼 있어 정규식으로 안전하게 뽑을 수 있다.
_PLAN_RE = re.compile(
    r'title:"((?:[^"\\]|\\.)*)",operationType:\{[^}]*\},renewable:\w,price:(\d+)'
)


def fetch_fanding_vtuber_creators(session: requests.Session) -> list[dict]:
    """팬딩 VTuber 카테고리 크리에이터 전체 목록. 공개 REST 엔드포인트, 로그인 불필요."""
    r = session.get(f"{FANDING_BASE}/rest/explorer/creator_list",
                     params=dict(iLimit=300, iMainCategoryNo=FANDING_VTUBER_CATEGORY_NO),
                     timeout=20)
    r.raise_for_status()
    j = r.json()
    data = j.get("aData", {})
    creators = data.get("aCreatorList", [])
    total = data.get("iTotalCount", len(creators))
    if len(creators) < total:
        print(f"  ⚠ 크리에이터 목록이 iLimit=300으로도 전체({total})를 못 채웠다 — "
              f"받은 {len(creators)}개만 사용")
    return [dict(
        creator_url=c["sCreatorUrl"], nickname=c["sNickname"],
        description=c.get("sOneLineDescription") or "",
        main_category=c.get("sMainCategoryCode"), sub_category=c.get("sSubCategoryCode"),
    ) for c in creators]


def fetch_fanding_membership_tiers(session: requests.Session, creator_url: str) -> list[tuple[str, int]]:
    """크리에이터의 공개 멤버십 페이지에서 (티어명, 가격원) 목록을 뽑는다.
    멤버십 탭이 비활성/티어 없음이면 빈 리스트(정상)."""
    url = f"{FANDING_BASE}/en/@{quote(creator_url)}/membership"
    r = session.get(url, timeout=20)
    if r.status_code != 200:
        return []
    return [(title, int(price)) for title, price in _PLAN_RE.findall(r.text)]


def collect_fanding(session: requests.Session) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("팬딩 VTuber 카테고리 크리에이터 목록 조회...")
    creators = fetch_fanding_vtuber_creators(session)
    print(f"  크리에이터 {len(creators)}명")

    tier_rows, ok, failed = [], 0, []
    for i, c in enumerate(creators, 1):
        try:
            tiers = fetch_fanding_membership_tiers(session, c["creator_url"])
        except requests.RequestException as e:
            failed.append(c["creator_url"])
            print(f"  [{i}/{len(creators)}] {c['nickname']:20s} 실패({e})")
            time.sleep(0.3)
            continue
        ok += 1
        for idx, (title, price) in enumerate(tiers):
            tier_rows.append(dict(
                creator_url=c["creator_url"], nickname=c["nickname"],
                tier_index=idx, tier_title=title, price_krw=price,
            ))
        if i % 20 == 0 or i == len(creators):
            print(f"  [{i}/{len(creators)}] 진행 중... (티어 확보 {len(tier_rows)}건)")
        time.sleep(0.3)  # 예의상 지연 — 111개 페이지를 초당 여러 건 두드리지 않는다

    creators_df = pd.DataFrame(creators)
    tiers_df = pd.DataFrame(tier_rows)
    print(f"완료: 크리에이터 {ok}/{len(creators)}명 조회 성공(실패 {len(failed)}), "
          f"멤버십 티어 {len(tiers_df)}건 확보")
    return creators_df, tiers_df


# ---------------------------------------------------------------------------
# 레이어 2 · 텀블벅 크라우드펀딩 (정적 큐레이션 — 위 docstring 참고)
#   goal_estimated=True인 행은 텀블벅 프로젝트 페이지가 "모인금액·후원자·달성률"만
#   보여주고 목표금액 자체를 표시하지 않아 달성률로 역산한 값이다(실제 목표와
#   반올림 오차가 있을 수 있음). False인 행(이세계아이돌 2건)은 언론이 목표금액을
#   "2000만원"으로 명시 보도해 역산이 아니다.
# ---------------------------------------------------------------------------
CROWDFUNDING_PROJECTS = [
    dict(
        project_name="마법소녀 이세계아이돌 단행본 & 스페셜 굿즈", org="이세계아이돌(패러블엔터테인먼트)",
        category="공식 굿즈 펀딩", platform="텀블벅", slug="magicalgirl_isegyeidol",
        period_start="2023-12-28", period_end="2024-01-25",
        goal_krw=20_000_000, goal_estimated=False,
        raised_krw=4_198_890_740, backers=31_336,
        source_url="https://namu.wiki/w/%EB%A7%88%EB%B2%95%EC%86%8C%EB%85%80%20%EC%9D%B4%EC%84%B8%EA%B3%84%EC%95%84%EC%9D%B4%EB%8F%8C ; "
                    "https://sports.khan.co.kr/article/202401261010003",
        source_type="언론 보도 + 나무위키 (텀블벅 자체·언론이 사후 발표한 최종 집계, 2024-01-26 보도 기준)",
        note="당시 국내 크라우드펀딩 역사상 최대 후원액으로 보도됨. 오픈 24시간 만에 25.3억원 돌파.",
    ),
    dict(
        project_name="차원을 넘어 이세계아이돌 단행본 & 굿즈", org="이세계아이돌(패러블엔터테인먼트)",
        category="공식 굿즈 펀딩", platform="텀블벅", slug="beyondthedimension_isedol",
        period_start="2024-10-23", period_end="2024-11-22",
        goal_krw=20_000_000, goal_estimated=False,
        raised_krw=8_822_342_758, backers=35_600,
        source_url="https://namu.wiki/w/%EC%B0%A8%EC%9B%90%EC%9D%84%20%EB%84%98%EC%96%B4%20%EC%9D%B4%EC%84%B8%EA%B3%84%EC%95%84%EC%9D%B4%EB%8F%8C ; "
                    "https://www.asiae.co.kr/article/2024112710003515336",
        source_type="언론 보도 + 나무위키 (텀블벅 자체·언론이 사후 발표한 최종 집계, 2024-11-27 보도 기준)",
        note="위 '마법소녀 이세계아이돌' 기록을 경신하며 역대 1위 등극. 오픈 23분 만에 이전 최고 기록 경신.",
    ),
    dict(
        project_name="유니버스 데뷔 3주년 기념 광고 프로젝트", org="스텔라이브(팬 제작·비공식)",
        category="팬메이드 광고 펀딩", platform="텀블벅", slug="stelluniverse3",
        period_start="2026-03-01", period_end="2026-03-31",
        goal_krw=8_000_000, goal_estimated=True,
        raised_krw=37_856_556, backers=973,
        source_url="https://tumblbug.com/stelluniverse3",
        source_type="텀블벅 프로젝트 페이지 직접 열람(2026-08-12)",
        note="스텔라이브 2기생(UNIVERSE) 팬이 기획·운영. 회사 공식 계정이 아니다(2차창작 가이드라인 "
             "범위 내 사전 승인). 최종 정산액 34,114,780원(플랫폼 수수료 약 9.9% 차감) 전액을 광고비· "
             "일러스트레이터 외주비로 지출했다고 창작자가 정산 내역을 공개 — 이 돈은 스텔라이브 회사 "
             "매출로 잡히지 않는다.",
    ),
    dict(
        project_name="2026 사키하네 후야 생일 광고", org="스텔라이브(팬 제작·비공식)",
        category="팬메이드 광고 펀딩", platform="텀블벅", slug="happy_huya_day",
        period_start="2026-04-01", period_end="2026-04-29",
        goal_krw=10_000_000, goal_estimated=True,
        raised_krw=30_244_027, backers=693,
        source_url="https://tumblbug.com/happy_huya_day",
        source_type="텀블벅 프로젝트 페이지 직접 열람(2026-08-12)",
        note="스텔라이브 멤버 개인 생일 기념 팬메이드 광고 펀딩.",
    ),
    dict(
        project_name="2026 아라하시 타비 생일 광고", org="스텔라이브(팬 제작·비공식)",
        category="팬메이드 광고 펀딩", platform="텀블벅", slug="2026tabi_birthday",
        period_start="2026-05-25", period_end="2026-06-24",
        goal_krw=5_700_000, goal_estimated=True,
        raised_krw=26_810_200, backers=920,
        source_url="https://tumblbug.com/2026tabi_birthday",
        source_type="텀블벅 프로젝트 페이지 직접 열람(2026-08-12)",
        note="스텔라이브 멤버 개인 생일 기념 팬메이드 광고 펀딩.",
    ),
    dict(
        project_name="[팬메이드] 2026 하나코 나나 생일 광고", org="스텔라이브(팬 제작·비공식)",
        category="팬메이드 광고 펀딩", platform="텀블벅", slug="20260807",
        period_start="2026-04-20", period_end="2026-05-20",
        goal_krw=8_000_000, goal_estimated=True,
        raised_krw=22_576_103, backers=523,
        source_url="https://tumblbug.com/20260807",
        source_type="텀블벅 프로젝트 페이지 직접 열람(2026-08-12)",
        note="스텔라이브 멤버 개인 생일 기념 팬메이드 광고 펀딩.",
    ),
]


def collect_crowdfunding() -> pd.DataFrame:
    df = pd.DataFrame(CROWDFUNDING_PROJECTS)
    df["achievement_pct"] = (df["raised_krw"] / df["goal_krw"] * 100).round(1)
    df["per_backer_krw"] = (df["raised_krw"] / df["backers"]).round(0).astype(int)
    return df


# ---------------------------------------------------------------------------
# 레이어 3 · 09_dart_financials 재무제표 읽기 전용 재사용 (DART 재수집 없음)
# ---------------------------------------------------------------------------
FAN_ADJACENT_COMPANIES = ["샌드박스네트워크", "패러블엔터테인먼트"]


def load_financials() -> pd.DataFrame:
    if not PROJECT09_METRICS.exists():
        print(f"  ⚠ {PROJECT09_METRICS} 없음 — 09_dart_financials/analyze.py를 먼저 실행해야 한다")
        return pd.DataFrame()
    df = pd.read_csv(PROJECT09_METRICS)
    out = df[df["corp_name"].isin(FAN_ADJACENT_COMPANIES)].copy()
    print(f"  09_dart_financials/data/company_metrics.csv 읽기 전용 재사용: "
          f"{FAN_ADJACENT_COMPANIES} {len(out)}행")
    return out


def collect() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    creators_df, tiers_df = collect_fanding(session)
    creators_df.to_csv(DATA / "fanding_creators.csv", index=False)
    tiers_df.to_csv(DATA / "fanding_tiers.csv", index=False)

    print("\n텀블벅 크라우드펀딩 데이터셋 구성(정적 큐레이션 — 위 docstring 참고)...")
    cf_df = collect_crowdfunding()
    cf_df.to_csv(DATA / "crowdfunding_projects.csv", index=False)
    print(f"  프로젝트 {len(cf_df)}건")

    print("\n09_dart_financials 재무제표 재사용...")
    fin_df = load_financials()
    fin_df.to_csv(DATA / "company_financials.csv", index=False)

    n_creators_with_tiers = tiers_df["creator_url"].nunique() if len(tiers_df) else 0
    meta = dict(
        fetched_at=datetime.now(timezone.utc).isoformat(),
        source="팬딩(Fanding) 공개 REST(/rest/explorer/creator_list, /@.../membership) + "
               "텀블벅(Tumblbug) 공개 결과 정적 큐레이션(로봇배제표준상 /api/ 자동수집 불가) + "
               "09_dart_financials 재사용(DART 재수집 없음)",
        n_fanding_creators=len(creators_df),
        n_fanding_creators_with_tiers=n_creators_with_tiers,
        n_fanding_tiers=len(tiers_df),
        n_crowdfunding_projects=len(cf_df),
        n_financial_company_years=len(fin_df),
        tumblbug_blocked_by_robots=True,
        tumblbug_robots_rule="Disallow: /api/  (https://tumblbug.com/robots.txt) — 실제 모금액/후원자 "
                              "수치는 전부 이 경로에서만 온다. 상세 페이지 HTML은 클라이언트 렌더링 "
                              "껍데기라 requests만으로는 수치를 읽을 수 없다.",
        wadiz_note="robots.txt는 개별 캠페인 페이지를 막지 않지만, VTuber 카테고리 캠페인 자체가 "
                    "검색상 사실상 없어(국내 버튜버 크라우드펀딩은 텀블벅에 쏠림) 이 프로젝트에서는 다루지 않음",
    )
    (DATA / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n완료 -> {DATA}")


if __name__ == "__main__":
    collect()
