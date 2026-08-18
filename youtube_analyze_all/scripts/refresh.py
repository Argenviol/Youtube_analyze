"""
프로젝트 수집→분석→사이트 재생성을 묶어서 돌린다.
작업 스케줄러(M5)가 그대로 호출하는 진입점이다.

  python scripts/refresh.py --group live      # 08 동시시청자 (10분)
  python scripts/refresh.py --group daily     # 01·02·03·06
  python scripts/refresh.py --group weekly    # 04·05·10·11
  python scripts/refresh.py --group monthly   # 09 DART (공시 주기가 분기·연간)
  python scripts/refresh.py --group all       # 전부
  python scripts/refresh.py --group daily --skip-collect   # 수집 없이 재분석만

## YouTube 쿼터 메모
실측 기준 소모량 (한도: 10,000 units/일 + search.list 별도 100회/일).

  04 키리누키  search 33회 = 3,300 units   ← 유일하게 비싼 프로젝트
  02 커버곡    search  0회 =   ~173 units   (2026-08-12 전량 열거로 전환)
  01/06        search  0회 =    ~40 units
  05 댓글      search  0회 =    ~50 units
  --------------------------------------------
  daily 전체   search  0회 =   ~250 units   → 매일 돌려도 한도의 2.5%

04만 search.list 에 의존해 weekly 로 남겼다. 02와 같은 방식(업로드 재생목록 전량 열거)으로
바꾸면 04도 daily 로 내릴 수 있지만, 04는 **남의 채널**에서 키리누키를 찾는 것이라
채널 목록을 미리 알 수 없어 검색이 불가피하다. 성격이 다른 문제다.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GROUPS = {
    "live":     ["08_live_viewership"],
    # 02는 원래 search.list 를 써서 3,300 units 를 먹는 weekly 대상이었으나,
    # 2026-08-12 업로드 재생목록 전량 열거로 바꾸면서 ~173 units 로 떨어져 daily 로 옮겼다.
    # 07은 06의 group_summary.csv 를 읽어 시장 리포트를 만든다. 반드시 06 뒤에 온다
    # (이 리스트 순서가 곧 실행 순서다). 자체 수집은 없고 재분석만 한다 — NO_COLLECT 참고.
    "daily":    ["01_member_channel_performance", "02_cover_song_ranking",
                 "03_chzzk_stream_pattern", "06_competitor_comparison",
                 "07_market_analysis"],
    "weekly":   ["04_kirinuki_ecosystem", "05_comment_sentiment",
                 "10_hoyoverse", "11_fan_commerce"],
    # 09는 DART 공시 주기를 따른다. 재무제표는 분기·연간 단위로만 갱신되므로
    # 자주 돌려봐야 같은 숫자를 다시 받을 뿐이고, 감사보고서 원문(ZIP) 파싱이
    # 무거워서 월 1회로 충분하다.
    "monthly":  ["09_dart_financials"],
}
GROUPS["all"] = GROUPS["daily"] + GROUPS["weekly"] + GROUPS["monthly"] + GROUPS["live"]

# 08은 --once 로 스냅샷 1회만 찍는다. 나머지는 인자 없이 전량 수집.
COLLECT_ARGS = {"08_live_viewership": ["--once"]}

# 수집 단계만 건너뛰고 분석·사이트 생성은 그대로 도는 프로젝트.
#
# 07은 외부 리서치(웹서치로 모은 공개 시장 통계) 기반이라 자동 수집이 불가능하다.
# 그렇다고 그룹에서 아예 빼면 안 된다 — 07은 06의 group_summary.csv 를 읽어 쓰는데,
# 06이 daily 로 갱신되는 동안 07만 안 돌면 두 프로젝트가 서로 다른 숫자를 말하게 된다.
# 실제로 그랬다: 06이 평균 최근 조회수 148,356 을 들고 있을 때 07은 155,586 이었다.
NO_COLLECT = {"07_market_analysis"}


def run(project: str, script: str, extra: list[str] | None = None) -> tuple[bool, str]:
    path = ROOT / project / script
    if not path.exists():
        return True, f"    (건너뜀: {script} 없음)"
    cmd = [sys.executable, str(path)] + (extra or [])
    started = time.time()
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    dur = time.time() - started
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-4:]
        return False, f"    ✗ {script} 실패 ({dur:.0f}초)\n" + "\n".join(f"      {t}" for t in tail)
    return True, f"    ✓ {script} ({dur:.0f}초)"


def main(group: str, skip_collect: bool) -> int:
    projects = list(GROUPS[group])
    started = datetime.now(timezone.utc)
    print(f"[refresh] group={group} 프로젝트 {len(projects)}개 · {started.isoformat()}")

    failures = []
    for proj in projects:
        print(f"\n  {proj}")
        collect = not skip_collect and proj not in NO_COLLECT
        steps = [("collect.py", COLLECT_ARGS.get(proj))] if collect else []
        steps += [("analyze.py", None), ("build_site.py", None)]

        for script, extra in steps:
            ok, msg = run(proj, script, extra)
            print(msg)
            if not ok:
                # 한 프로젝트가 죽어도 나머지는 계속 돌린다.
                failures.append(f"{proj}/{script}")
                break

    # 01·02·03·06 은 metrics CSV 를 덮어쓴다. 덮어쓰기 전이 아니라 후에 불러도
    # 되는 이유는, history.py 가 _meta.json 의 수집 날짜를 키로 쓰고 같은 날짜면
    # 교체하기 때문이다. 하루에 여러 번 돌아도 중복이 안 쌓인다.
    if group != "live":
        print("\n  지표 축적(history)")
        ok, msg = run(".", "scripts/history.py")
        print(msg)
        if not ok:
            failures.append("scripts/history.py")

    # 리포트·차트·대시보드가 갱신됐으니 `결과물/` 도 다시 만든다. 이걸 빼먹으면
    # 결과물 폴더가 조용히 옛 수치를 보여주게 된다 — 틀린 것보다 나쁘다.
    # 08(live)은 10분마다 도는데 매번 전량 복사할 이유가 없어 제외한다.
    if group != "live":
        print("\n  결과물 갱신")
        ok, msg = run(".", "scripts/build_deliverables.py")
        print(msg)
        if not ok:
            failures.append("scripts/build_deliverables.py")

    dur = (datetime.now(timezone.utc) - started).total_seconds()
    print(f"\n[refresh] 완료 {dur:.0f}초 · 성공 {len(projects)-len(failures)} / 실패 {len(failures)}")
    if failures:
        print("  실패: " + ", ".join(failures))
        return 1
    return 0


def loop(group: str, minutes: int, skip_collect: bool) -> int:
    """작업 스케줄러 없이 포그라운드로 계속 돌릴 때 쓴다.

    08(동시시청자)은 소급 수집이 불가능하므로, 이 루프가 멈춘 구간은 영구 공백이 된다.
    한 번의 실패로 루프가 죽지 않도록 예외를 삼키고 다음 주기를 기다린다.
    """
    print(f"[refresh] 루프 시작 — group={group}, {minutes}분 간격 (Ctrl+C로 종료)")
    while True:
        try:
            main(group, skip_collect)
        except Exception as e:
            print(f"[refresh] 주기 실패(계속 진행): {e}")
        time.sleep(minutes * 60)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=sorted(GROUPS), default="daily")
    ap.add_argument("--skip-collect", action="store_true", help="수집 없이 분석·사이트만 재생성")
    ap.add_argument("--loop", type=int, metavar="MINUTES",
                    help="지정 간격으로 계속 반복 (예: --group live --loop 10)")
    a = ap.parse_args()
    if a.loop:
        sys.exit(loop(a.group, a.loop, a.skip_collect))
    sys.exit(main(a.group, a.skip_collect))
