# 02 · 커버곡 성과

**질문** — 커버곡은 누가, 얼마나, 어떤 조합(솔로·콜라보)으로 성과를 내는가. 다작과 곡당 파괴력은 같은 축인가.

- 데이터: YouTube Data API — 멤버 채널 업로드 재생목록 **전량 열거** → 제목 필터로 커버 확정 → 영상 상세.
  여기에 "<이름> - Topic" 채널의 음원 판을 곡 단위로 합산
- 갱신: daily

## 실행

```bash
export YOUTUBE_API_KEY=...
python collect.py [--max-videos 3000]   # → data/covers.csv, cover_songs.csv, topic_*.csv
python analyze.py
python build_site.py
```

## 방법

- **커버 판별** — 제목에 `cover|커버|歌ってみた|불러봤/본` 토큰. 콜라보(`x`)는 소유 채널 기준으로 세어 이중 계산을 막는다.
- **왜 검색이 아니라 전량 열거인가 (2026-08-12)** — `search.list` 는 관련도 상위 N개 창만 줘서 같은 채널을 다시
  받아도 결과가 흔들렸고(34→29곡, 삭제가 아니라 랭킹 변동) 호출당 100 units 였다. 업로드 재생목록 열거는 결정적이고
  페이지당 1 unit 이다(3,300 → ~100 units). 이 경계 이전 스냅샷과 커버곡 수를 직접 비교하지 않는다.
- **한 곡은 한 곡으로** — 본편 MV·4K·3D 라이브·쇼츠·티저를 `common/songs.song_key` 로 한 곡으로 묶는다(`song_count`).
  같은 멤버·발매일 ±3일의 Topic 음원 판을 짝지어 더한 것이 `total_views_incl_topic`. 후보가 둘 이상이면 붙이지
  않고(`topic_pairs.csv` 의 `pair_reason`), 사람이 확정한 짝은 `data/topic_pairs_manual.csv` 가 우선한다.
- Topic 채널 ID 는 oEmbed 로 확인한 값(`TOPIC_SEED`)과 `search.list` 결과를 `data/topic_channels.json` 에 캐시하고,
  "없음"으로 확인된 멤버는 7일에 한 번만 다시 찾는다(`TOPIC_RECHECK_DAYS`).

## 산출물

| 경로 | 내용 |
|---|---|
| `data/covers.csv` · `cover_songs.csv` | 커버 영상 단위 · 곡 단위(판 합산·음원 포함) |
| `data/cover_metrics.csv` | 멤버별 집계 — `cover_count`(영상) · `song_count`(곡) · `total_views` · `topic_views` · `total_views_incl_topic` |
| `data/topic_channels.json` · `topic_tracks.csv` · `topic_pairs.csv` | Topic 채널 캐시 · 음원 트랙 · 짝짓기 결과 |
| `data/history.csv` | 날짜별 축적 |
| `sql/` · `charts/`(7종) · `site/` · `REPORT.md` | 공통 산출물 |

## 읽는 법 · 한계

- 곡 수 상위와 총 조회수·곡당 평균 상위는 일부만 겹친다 — 다작형과 소수정예형이 함께 있다. 겹치는 인원은 `REPORT.md`.
- 커버로 짝지어지지 않은 Topic 트랙은 대부분 오리지널곡 음원이고, 12 의 오리지널곡 효과에서 MV 조회수에 더해진다.
- 콜라보 커버는 2024년부터만 존재해 전체 기간 평균을 솔로와 비교하면 착시가 생긴다(12 참고).
