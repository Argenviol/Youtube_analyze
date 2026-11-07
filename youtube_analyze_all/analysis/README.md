# analysis — 분석을 진행하는 곳

[`../collect/`](../collect/)와 기존 프로젝트(01~08·12)의 `data/` 를 읽기만 한다. 수집 호출은 하지 않는다.
결과는 `out/` 에 마크다운·CSV 로 쓰고, 숫자는 전부 스크립트가 계산한다(손으로 적지 않는다).
`analyze-community` 워크플로가 수집 뒤·매주 일요일에 자동으로 다시 돌려 `out/` 을 커밋한다.

| 스크립트 | 질문 | 결과 |
|---|---|---|
| `origin_of_viewers.py` | 4기 데뷔 시청자는 어디서 왔나 | `out/origin_of_viewers.md` |
| `dc_reaction.py` | 4기 데뷔 전후 디시 갤러리 반응 | `out/dc_reaction.md` |
| `hypotheses.py` | 가설 H1~H6 (되는 만큼, 안 되면 사유와 함께 보류) | `out/hypotheses.md` |

가설 정의는 [`../../자료_점검_및_분석계획.md`](../../자료_점검_및_분석계획.md) 6절.
