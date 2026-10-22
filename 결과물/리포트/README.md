# 리포트 PDF

12개 프로젝트를 **두 권**(스텔라이브 팬덤 / 게임 캐릭터 인기도)으로 묶은 종합 리포트입니다. 소재가 다르면
문서를 나눕니다 — 한 권에 섞으면 읽는 사람이 중간에 맥락을 갈아타야 합니다. 각 권은 전체판과 요약판이 있습니다.

## 바로 보기

| 파일 | 내용 | 이런 분께 |
|---|---|---|
| [`StelLive-요약.pdf`](StelLive-요약.pdf) | 스텔라이브 11개 프로젝트(01~09·11·12) — 수집 데이터에서 계산된 숫자·표·차트만 | 결론 서술 없이 숫자만 보고 싶을 때 |
| [`StelLive-리포트.pdf`](StelLive-리포트.pdf) | 같은 11개 — 결론 서술·상세 분석·데이터 함정 포함 | 무엇을 발견했고 어떻게 검증했는지 읽을 때 |
| [`게임-요약.pdf`](게임-요약.pdf) | 다섯 게임(호요버스 4 + 블루 아카이브) 캐릭터 인기도 — 같은 규칙의 요약판 | |
| [`게임-리포트.pdf`](게임-리포트.pdf) | 게임 전체판 | |

요약판에서 뺀 것은 결론 문단과 상세 해석뿐입니다. 출처가 붙은 공개 자료 수치(07 시장 규모, 09 DART 재무)는
그대로 둡니다. 측정하지 못한 항목은 "측정 불가"로 남기고 추정치로 채우지 않습니다.

## 규격

- **페이지 150×210mm** — 휴대폰 화면에 맞춘 크기. A4 는 한 줄이 길어 확대·좌우 스크롤을 하게 됩니다.
- **서체 내장** — Noto Sans KR 한 가족(OFL, `youtube_analyze_all/common/fonts/`)을 HTML 에 base64 로 넣어
  어디서 열어도 같은 글자로 보입니다. 외부 폰트 링크를 쓰지 않습니다.
- **기준일** — 첫 장의 "생성" 날짜와 절마다 붙은 "기준" 배지. 수치는 그 시점의 스냅샷이며, 같은 그림은 문서
  전체에서 한 번만 실립니다.
- 자동 수집이 만들지 않는 **수동 산출물**입니다. 만든 날짜는 `HANDOVER.md` 에 있습니다.

## 다시 만들기

```bash
python youtube_analyze_all/scripts/build_unified.py            # 전체판 HTML → 결과물/_build/
python youtube_analyze_all/scripts/build_unified.py --digest   # 요약판 HTML
for k in StelLive-리포트 StelLive-요약 게임-리포트 게임-요약; do
  chromium --headless=new --no-pdf-header-footer --virtual-time-budget=8000 \
    --print-to-pdf="결과물/리포트/$k.pdf" "file://$PWD/결과물/_build/$k-print.html"
done
pdffonts 결과물/리포트/StelLive-요약.pdf    # emb = yes 인지 확인
```

`_build/` 는 파생물이라 git 에 올리지 않습니다. 디자인·서체·페이지 규격은 `build_unified.py` 의 CSS 한 곳에서
관리합니다. 바꾼 뒤에는 휴대폰 화면에서 읽히는지 확인합니다.
