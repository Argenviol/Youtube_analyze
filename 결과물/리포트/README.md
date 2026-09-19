# 리포트 PDF

`scripts/build_unified.py` 가 만든 HTML 을 헤드리스 크로미움으로 뽑은 PDF 입니다. 페이지는
휴대폰 화면에 맞춘 150×210mm 이고 한글 폰트가 파일 안에 들어 있습니다.

| 파일 | 내용 |
|---|---|
| `StelLive-요약.pdf` | 스텔라이브 11개 프로젝트 — 수집 데이터에서 계산된 숫자·표·차트만 (`--digest`) |
| `게임-요약.pdf` | 호요버스 4개 게임 캐릭터 인기도 — 같은 규칙의 요약판 |
| `StelLive-리포트.pdf` | 스텔라이브 전체판 — 결론 서술·상세 분석 포함 |
| `게임-리포트.pdf` | 게임 전체판 |

요약판에서 뺀 것은 결론 문단과 상세 해석뿐입니다. 공개 자료를 인용한 숫자(07 시장 규모, 09 DART
재무 등)는 출처가 붙어 있으므로 그대로 둡니다. 측정하지 못한 항목은 "측정 불가"로 남기고 추정치로
채우지 않습니다.

다시 만들려면:

```bash
python youtube_analyze_all/scripts/build_unified.py            # 전체판 HTML
python youtube_analyze_all/scripts/build_unified.py --digest   # 요약판 HTML
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=결과물/리포트/StelLive-요약.pdf file://$PWD/결과물/_build/StelLive-요약-print.html
```

기준일은 각 PDF 첫 장의 "생성" 날짜와 절마다 붙은 "기준" 배지에 있습니다.
