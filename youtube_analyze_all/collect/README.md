# collect — 정보를 모으는 곳

새로 들어오는 원천 자료만 둔다. 분석은 [`../analysis/`](../analysis/)에서 이 폴더의 `data/` 를 읽는다.
기존 01~08·12 프로젝트는 자기 폴더에서 수집·분석을 같이 하며 그대로 둔다.
전부 **GitHub Actions** 에서 돈다(API 키 불필요). 손으로 돌릴 때만 아래 명령을 쓴다.

| 스크립트 | 모으는 것 | 산출(`data/`) | 어디서 도나 |
|---|---|---|---|
| `chzzk_chat.py` | 치지직 다시보기 채팅 — 분당 채팅·후원 **건수**·구독 메시지·참여자 해시 | `chat_minutes.csv` · `chat_videos.csv` · `chatters/` | `collect-community` (매주 일요일 + 수동) |
| `dcinside.py` | 디시 갤러리 3곳(스텔라이브·버츄얼 스나·버츄얼 스트리머) 글 목록 | `dc_posts.csv` | `collect-community` (매주 + 수동, 기준일 입력) |
| `chzzk_vtubers.py` | 치지직 상위 500개 방송 합계 + 버튜버 후보 + 명단 채널 시청자 | `chzzk_total.csv` · `vtuber_candidates.csv` · `vtuber_ccu.csv` | `collect-vtubers` (매시간) |
| `shorts_snapshot.py` | 멤버 채널 최근 업로드 30개의 조회수(매일 한 줄씩, 시점별 이력) | `shorts_views.csv` | `collect-shorts` (매일) |
| `anime_season.py` | 다음 분기 TV 애니 일정(AniList) | `anime_season.csv` | `collect-community` 수동 |

## 버튜버 명단
`vtuber_roster.csv` (group, name, chzzk_id, note)에 **운영자가 확인한 채널만** 올린다. 집계는 이 명단만 센다.
제목·태그로 잡은 후보(`vtuber_candidates.csv`)는 참고일 뿐이다. 스텔라이브 15명은 08 이 재므로 넣지 않는다.
이세계아이돌·홀로라이브는 치지직이 아니라 숲·유튜브가 주 무대라 치지직 명단에서 확인되지 않았다.

## 못 모으는 것
- 후원 **금액** — 다시보기 채팅의 `payAmount` 는 항상 0.
- 다시보기 채팅은 **초당 ~20건(분당 ~1,240)까지만** 저장된다 — 4기 데뷔 방송은 이 한도에 붙어 있어 채팅 수는 하한이다.
- 눈팅 시청자, 시청자 유입 경로 — 치지직이 공개하지 않는다.
- OP/ED 곡·버튜버 발매 일정 — 모아둔 공개 출처가 없다.
- 닉네임·채팅 본문·디시 글쓴이는 일부러 저장하지 않는다.
