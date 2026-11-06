#!/usr/bin/env node
/**
 * data.json 동기화 스크립트 (M3).
 *
 * `youtube_analyze_all/<project>/site/data.json` (Python `analyze.py`가 생성한
 * 원본, source of truth)을 `app/src/data/<id>.json` 으로 복사한다.
 * Next.js 정적 export(`output: 'export'`)는 `app/` 디렉토리 밖의 파일을 import할
 * 수 없어서, 빌드 전에 이 스크립트로 데이터를 앱 안으로 들여온다.
 *
 * ⚠ `app/src/data/*.json` 은 전부 생성 파일이다. 손으로 고치지 말 것 — 다음
 *   `npm run sync` (또는 `npm run build`, prebuild 훅으로 자동 실행됨) 실행 시
 *   덮어써진다. 값을 바꾸고 싶으면 해당 프로젝트의 `analyze.py`를 고쳐서
 *   `site/data.json`을 재생성해야 한다.
 *
 * 사용:
 *   npm run sync            (내부적으로 `node scripts/sync-data.mjs` 실행)
 *
 * 실패 처리: REQUIRED_PROJECTS의 소스 파일이 하나라도 없으면 즉시 비정상
 * 종료(exit 1)한다. 일부만 복사된 채로 조용히 넘어가면 "부분적으로 오래된"
 * 앱이 빌드되는 최악의 상태가 되기 때문이다.
 *
 * 대상 프로젝트: 01·02·03·04·05·06·08. 07(시장 분석)은 외부 리서치 기반 정적 페이지로 앱 라우트에
 * 포함하지 않으므로(PRD §4 "앱에서 제외") 동기화 대상에서 제외한다.
 */
import { existsSync, mkdirSync, copyFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const APP_ROOT = join(__dirname, ".."); // app/
const REPO_ROOT = join(APP_ROOT, ".."); // 클로드 코드/ (저장소 루트, git 없음)
const SOURCE_ROOT = join(REPO_ROOT, "youtube_analyze_all");
const DEST_DIR = join(APP_ROOT, "src", "data");

/** [source 디렉토리명, 앱에서 쓸 짧은 id] — 없으면 빌드를 중단시키는 필수 프로젝트. */
const REQUIRED_PROJECTS = [
  ["01_member_channel_performance", "01"],
  ["02_cover_song_ranking", "02"],
  ["03_chzzk_stream_pattern", "03"],
  ["04_kirinuki_ecosystem", "04"],
  ["05_comment_sentiment", "05"],
  ["06_competitor_comparison", "06"],
  ["08_live_viewership", "08"],
];

mkdirSync(DEST_DIR, { recursive: true });

let failed = false;
const copied = [];

for (const [sourceDirName, id] of REQUIRED_PROJECTS) {
  const src = join(SOURCE_ROOT, sourceDirName, "site", "data.json");
  const dest = join(DEST_DIR, `${id}.json`);

  if (!existsSync(src) || !statSync(src).isFile()) {
    console.error(`[sync-data] 누락: ${src}`);
    failed = true;
    continue;
  }

  copyFileSync(src, dest);
  copied.push(`${sourceDirName}/site/data.json -> src/data/${id}.json`);
}

if (failed) {
  console.error(
    "[sync-data] 필수 소스 파일이 하나 이상 없어 중단합니다. " +
      "부분적으로만 최신인 빌드를 만들지 않기 위해 실패 처리합니다."
  );
  process.exit(1);
}

for (const line of copied) console.log(`[sync-data] ${line}`);
console.log(
  `[sync-data] 완료 — ${REQUIRED_PROJECTS.length}개 프로젝트 처리`
);
