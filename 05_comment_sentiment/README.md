# 프로젝트 5 · StelLive 댓글 여론/감성 분석

멤버별 인기 영상의 상위 댓글을 수집하고, **Claude가 직접 문맥을 읽어** 감성(긍정/중립/부정)과
토픽(7종)으로 분류합니다. 규칙 기반 키워드 매칭이 아니라 반어법·팬덤 용어·자조적 유머를
고려한 판단입니다.

## 실행 방법

```bash
pip install -r ../requirements.txt
export YOUTUBE_API_KEY="발급받은_키"

python collect.py --videos-per-member 4 --comments-per-video 40
# -> data/comments_raw.csv (1753개), data/comments_sample.csv (좋아요 상위 330개 표본)

# 표본 라벨링은 Claude가 수행 (본 저장소는 이미 라벨링된 comments_labeled.csv 포함)
# 재현하려면: comments_sample.csv를 Claude(API/대화)에게 sentiment/topic 분류 요청

python analyze.py     # SQL/차트/리포트/사이트 데이터
python build_site.py  # site/index.html
```

## 방법론

1. 멤버별 조회수 상위 영상 4개 선정 → 각 영상 추천순(relevance) 상위 댓글 최대 40개 수집(1,753개).
2. 4자 미만 초단문(이모지 등) 제외.
3. **좋아요 수 상위 30개/멤버(총 330개)** 를 표본으로 Claude가 직접 읽고 라벨링:
   - `sentiment`: positive / neutral / negative
   - `topic`: 목소리·노래 / 성격·개그 / 비주얼·디자인 / 방송내용·게임 / 멤버 케미 / 성장·추억 / 기타
4. 표본 기준 집계로 멤버별 감성 점수(긍정비율−부정비율) 산출.

## 산출물

| 경로 | 내용 |
|------|------|
| `data/comments_raw.csv` | 원천 댓글 1,753개 |
| `data/comments_sample.csv` | 좋아요 상위 330개 표본(라벨링 전) |
| `data/comments_labeled.csv` | Claude 라벨링 결과(sentiment·topic 포함) |
| `data/sentiment_metrics.csv` | 멤버별 감성 집계 |
| `sql/` | `comments`/`sentiment_metrics` 스키마·INSERT·분석쿼리·SQLite·실행결과 |
| `charts/*.png` | 차트 4종(감성점수·감성구성·토픽분포·멤버×토픽 히트맵) |
| `site/index.html` | 인터랙티브 대시보드 |

## 주요 결과 (수집 시점 스냅샷)

- 표본 전체 **긍정 80% / 중립 18% / 부정 2%** — 추천순 상위 댓글은 팬 애정 표현이 압도적.
- **감성 점수 1위**: 네네코 마시로·유즈하 리코 (+93점, 부정 0%).
- 가장 많이 언급되는 토픽: **성격·개그(91건)**, **방송내용·게임(88건)** — 목소리·노래(31건)보다 우위.
- 부정 댓글은 대부분 "몸매 걱정" 류의 애정 어린 우려이거나 주제 이탈성 댓글.

> 한계: 추천순(relevance) 알고리즘은 재치있고 공감받는 댓글을 우선 노출하는 경향이 있어
> 무작위 표본보다 긍정 편향될 수 있습니다.
