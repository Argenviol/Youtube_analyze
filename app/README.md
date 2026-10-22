# 통합 대시보드 (`app/`)

`youtube_analyze_all/` 의 분석 파이프라인이 만든 `site/data.json` 을 읽어 **필터·드릴다운이 되는 한
사이트**로 묶는 Next.js(App Router · TypeScript) 앱입니다. 정적 export 라 서버가 없고, 외부 차트·UI
라이브러리와 CDN 을 쓰지 않아 오프라인에서도 동작합니다. 요구사항은 [`../PRD.md`](../PRD.md).

## 실행

```bash
cd app
npm install
npm run dev            # http://localhost:3000
npm run build          # prebuild 가 data.json 을 동기화한 뒤 out/ 에 정적 export
npm run lint
```

- **`out/` 은 HTTP 로 서빙해야 합니다.** 에셋을 `/_next/...` 절대경로로 참조해 `file://` 로 열면 아무것도
  로드되지 않습니다(`../.claude/launch.json` 의 `app-static`).
- GitHub Pages 하위 경로에 올릴 때는 `NEXT_PUBLIC_BASE_PATH=/저장소이름 npm run build`.

## 페이지

| 경로 | 내용 |
|---|---|
| `/` | 허브 — 핵심 발견 카드, 프로젝트 카드, 갱신 시각 |
| `/projects/01-channel` · `02-cover` · `03-stream` · `04-kirinuki` · `05-sentiment` · `06-competitor` · `08-live` | 멤버 단위 프로젝트 — 전역 필터(멤버·유닛·기간)와 멤버 상세 패널이 걸림 |
| `/projects/09-dart` · `10-hoyoverse` · `11-commerce` | 회사·게임·커머스 단위 프로젝트 — 멤버 필터 없음 |
| `/methodology` | 수집 방법과 실제로 만난 데이터 함정 |

07 시장 분석은 외부 리서치 기반이라 앱에 넣지 않고 기존 정적 페이지로 링크만 겁니다. 12 이벤트
임팩트는 `결과물/` 과 PDF 에서 봅니다.

## 데이터 흐름

```
youtube_analyze_all/<project>/site/data.json   ← Python analyze.py 가 생성 (정본)
        ↓ npm run sync (= prebuild, scripts/sync-data.mjs)
app/src/data/<id>.json                          ← 생성 파일. 손으로 고치지 않는다
```

- Python 이 수집·분석하고 JSON 을 내며, 앱은 읽어서 그리기만 합니다. 역할을 섞지 않습니다.
- 조인 키는 `name_en`. 로스터 정본은 `youtube_analyze_all/common/config.py` 이고 `src/data/roster.ts` 가
  같은 내용을 미러링합니다 — 멤버가 바뀌면 둘 다 고칩니다.
- 스키마는 [`src/data/contract.md`](src/data/contract.md). 갱신 주기 표시(`src/data/refresh.ts`)는
  `scripts/refresh.py` 의 `GROUPS` 와 맞춰 둡니다.

## 구조

```
src/
  app/                 페이지 (layout.tsx, page.tsx, projects/*, methodology/)
  components/          Card · StatTile · Table(정렬·pageSize) · Badge · FilterBar · FilterChip ·
                       Section · Freshness · MemberDetail · ThemeToggle · charts/(Bar·Line·Scatter·HeatMap, SVG 직접 구현)
  lib/                 useFilters(URL 쿼리와 동기화) · overlap(요약 문장)
  data/                roster.ts · types.ts · projects.ts · aggregate.ts · refresh.ts · <id>.json(생성)
  design/tokens.ts     Montage 디자인 토큰
scripts/sync-data.mjs  data.json 동기화
```

## 디자인

- 토큰은 [Montage](https://github.com/wanteddev/montage-web)(Wanted Lab, MIT)의 값입니다. 컴포넌트 패키지
  `@wanteddev/wds` 는 GitHub Packages 전용이라 설치하지 않고, `youtube_analyze_all/common/montage.py` 에
  있는 토큰 값을 `src/design/tokens.ts` 와 `globals.css` 로 옮겨 컴포넌트를 직접 만들었습니다.
- 테마는 셋 — 라이트(기본), 시스템 다크(`prefers-color-scheme`, 사용자가 라이트를 고르지 않은 경우),
  사용자 선택 다크(`<html data-theme>`, `localStorage`).
- 모든 UI 카피는 한국어. 넓은 표는 자체 컨테이너 안에서만 가로 스크롤하고 페이지 본문은 가로로 넘치지
  않습니다. 수백 행짜리 표는 `Table` 의 `pageSize` 로 나눠 그립니다(느린 기기에서 스크롤이 끊기지 않게).

## 확인 기준

변경 뒤에는 `npm run lint`·`npm run build` 통과와 함께 폰(390px)·PC 화면, 그리고 CPU 를 느리게 한
상태에서 화면 전환·스크롤·패널 열기가 끊기지 않는지를 봅니다(`../CLAUDE.md` 의 "최적화" 기준).
