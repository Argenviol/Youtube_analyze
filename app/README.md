# StelLive 팬덤 애널리틱스 — 대시보드 (M1)

`youtube_analyze_all/`의 분석 파이프라인이 만든 `data.json`들을 정적으로 렌더하는
Next.js 허브. PRD는 `../PRD.md` 참고. 이 마일스톤(M1)은 스캐폴드 + 디자인 토큰 +
허브 골격까지만 다룬다. 실제 데이터 연결(`data.json` 임포트)은 M3다.

## 실행 방법

```bash
cd app
npm install
npm run dev
```

<http://localhost:3000> 에서 확인한다.

정적 export 빌드(GitHub Pages 배포용):

```bash
npm run build
```

`out/` 디렉터리에 정적 HTML/CSS/JS가 생성된다. `next.config.ts`에서
`output: "export"`, `images.unoptimized: true`를 설정했다.

GitHub Pages 하위 경로(`https://<user>.github.io/<repo>/`)에 배포할 때는
`NEXT_PUBLIC_BASE_PATH` 환경변수로 저장소 이름을 넘긴다. 로컬 개발/루트 배포에서는
비워 두면 된다.

```bash
NEXT_PUBLIC_BASE_PATH=/repo-name npm run build
```

## 디렉터리 구조

```
app/
  src/
    app/            App Router 페이지 (page.tsx, layout.tsx, globals.css)
    components/     Card, StatTile, Table, Badge, FilterChip, Section, ThemeToggle
    design/
      tokens.ts     Montage 디자인 토큰 (TypeScript)
    data/           M3에서 <project>.json을 이곳에 둔다 (현재 비어 있음)
```

## Montage 디자인 토큰 — 왜 패키지를 설치하지 않았는가

이 프로젝트의 시각 언어는 원티드랩의 Montage(Wanted Design System for Web,
<https://github.com/wanteddev/montage-web>, MIT 라이선스)를 따른다.

Montage의 React 컴포넌트 라이브러리 `@wanteddev/wds`는 공개 npm 레지스트리에
배포되지 않고 **GitHub Packages 전용**으로 배포된다
(`publishConfig.registry: https://npm.pkg.github.com/`). 무인증 접근은 401을
반환하며, 원티드랩 조직 패키지가 외부에 공개돼 있는지도 사전에 확인할 수 없다
(토큰을 발급받아도 403이 날 수 있다).

따라서 컴포넌트 라이브러리를 설치하는 대신, `youtube_analyze_all/common/montage.py`에
이미 추출돼 있던 실제 토큰 값(atomic 팔레트, light/dark 시맨틱 컬러, 11색 accent,
spacing, radius, shadow, Pretendard 폰트 스택)을 `app/src/design/tokens.ts` +
`app/src/app/globals.css`로 그대로 옮기고, 컴포넌트는 그 토큰만으로 직접 구현했다.

이 방식의 장점:

- 외부 레지스트리 인증이 필요 없어 CI/로컬 빌드가 항상 오프라인으로 성공한다.
- 시각적 결과물은 실제 토큰 값을 그대로 쓰므로 사실상 동일하다.
- 값의 원본(source of truth)이 하나(`montage.py`)로 유지되고, TS/CSS는 그 값을
  미러링한 것임을 각 파일 주석에 명시했다.

단점: Montage 컴포넌트가 제공하는 접근성·모션·반응형 디테일까지 자동으로 따라오지는
않는다. 이 프로젝트에서는 Card / StatTile / Table / Badge / FilterChip / Section /
ThemeToggle을 토큰 기반으로 직접 구현해 채웠다.

## 테마

`globals.css`는 세 가지 상태를 지원한다.

1. bare `:root` — 라이트 팔레트 (기본값)
2. `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { ... } }`
   — 시스템이 다크이고 사용자가 명시적으로 라이트를 고르지 않은 경우
3. `:root[data-theme="dark"]` — 사용자가 다크를 직접 선택한 경우 (헤더의 테마
   토글이 `localStorage`에 저장하고 `<html data-theme>`을 갱신한다)

## 제약

- 외부 차트/UI 라이브러리, CDN 참조를 쓰지 않는다 (오프라인 동작 필수).
- 모든 UI 카피는 한국어.
- 넓은 표는 자체 `overflow-x: auto` 컨테이너 안에서만 스크롤하고, 페이지 본문은
  가로 스크롤되지 않는다.
