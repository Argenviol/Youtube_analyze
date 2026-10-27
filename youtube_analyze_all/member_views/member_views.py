"""멤버별 유튜브·노래 조회수 (루트 `멤버별_조회수_2026-10-25.md` 의 원본 계산).

API 키·쿼터 없이 유튜브 웹(innertube)에서 받는다.
  1. 업로드 재생목록 `UU…` 를 `youtubei/v1/browse` continuation 으로 전부 나열
  2. 영상마다 `youtubei/v1/next` 의 `videoViewCountRenderer`(정확한 조회수)·`dateText`
  3. `youtube.com/shorts/{id}` 가 200 이면 쇼츠(리다이렉트면 일반 영상)
노래 목록은 Argenviol/stel-database `app.js` 의 `SONG_DATA`(리제 키는 `rize`).

  python member_views.py fetch <key> <채널ID UC…> [SONG_DATA 키] [--app ../stel-database/app.js]
  python member_views.py stats <key>          # 멤버 하나 상세
  python member_views.py summary              # 10명 요약표 (문서의 표 1·2)
결과는 data/<key>_full.json(채널 영상 전부)·data/<key>_songs.json(노래 통계 곡).
"""
import argparse, concurrent.futures as cf, json, re, statistics as st, unicodedata, urllib.error, urllib.request
from pathlib import Path

DATA = Path(__file__).parent / "data"
CTX = {"client": {"clientName": "WEB", "clientVersion": "2.20251020.00.00", "hl": "ko", "gl": "KR"}}
CUTOFF = (2026, 10, 25)
RECENT_FROM = (2025, 10, 26)
# 노래 통계에 없지만 노래인 영상(커버 쇼츠·3D 라이브 커버·노래 모음) — 영상 평균에서 뺀다
NOT_VIDEO = re.compile(r"cover|커버|Playlist|메들리|music video|\bMV\b|歌ってみた|Aiobahn Remix|유니의 SUPERPOWER", re.I)
MEMBERS = [("yuni", "유니"), ("huya", "후야"), ("hina", "히나"), ("mashiro", "마시로"), ("lize", "리제"),
           ("tabi", "타비"), ("shibuki", "시부키"), ("rin", "린"), ("nana", "나나"), ("riko", "리코")]


def _post(ep, body):
    req = urllib.request.Request(f"https://www.youtube.com/youtubei/v1/{ep}?prettyPrint=false",
                                 json.dumps({"context": CTX, **body}).encode(), {"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=30).read().decode()


def list_uploads(channel_id):
    seen, out, body = set(), [], {"browseId": "VLUU" + channel_id[2:]}

    def walk(o):
        if isinstance(o, dict):
            lv = o.get("lockupViewModel")
            if lv and lv.get("contentId") and lv["contentId"] not in seen:
                seen.add(lv["contentId"])
                title = lv.get("metadata", {}).get("lockupMetadataViewModel", {}).get("title", {}).get("content", "")
                out.append({"id": lv["contentId"], "title": title})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    while body:
        s = _post("browse", body)
        walk(json.loads(s))
        tok = re.findall(r'"continuationItemViewModel".{0,1500}?"token":"([^"]+)"', s)
        body = {"continuation": tok[0]} if tok else None
    return out


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def video_info(v):
    err = ""
    for _ in range(3):
        try:
            s = _post("next", {"videoId": v["id"]})
            m = re.search(r'"videoViewCountRenderer":\{"viewCount":\{(?:"simpleText":"([^"]+)"|"runs":\[\{"text":"([^"]+)")', s)
            d = re.search(r'"dateText":\{"simpleText":"([^"]+)"', s)
            if not (m and d):
                raise ValueError("조회수·날짜 없음")
            n = int(re.sub(r"\D", "", m.group(1) or m.group(2)))
            try:
                sh = urllib.request.build_opener(_NoRedirect).open(
                    urllib.request.Request("https://www.youtube.com/shorts/" + v["id"], method="HEAD"), timeout=20).status == 200
            except urllib.error.HTTPError:
                sh = False
            return {**v, "views": n, "date": d.group(1), "shorts": int(sh)}
        except Exception as e:  # 일시 오류는 다시 시도, 세 번 실패하면 err 로 남긴다
            err = str(e)
    return {**v, "views": None, "date": "", "shorts": -1, "err": err}


def song_items(app_js, song_key):
    line = re.search(song_key + r":\{orig.*?\]\},", Path(app_js).read_text(encoding="utf-8")).group(0)
    pos = {k: line.index(k + ":[") for k in ("orig", "game", "multi", "cover")}
    return [{"id": m[2], "title": m[1], "kind": max((p, k) for k, p in pos.items() if p < m.start())[1]}
            for m in re.finditer(r't:"([^"]*)",id:"([^"]+)"', line)]


def fetch(key, channel_id, song_key, app_js):
    DATA.mkdir(exist_ok=True)
    with cf.ThreadPoolExecutor(8) as ex:
        for name, items in (("full", list_uploads(channel_id)), ("songs", song_items(app_js, song_key))):
            rows = list(ex.map(video_info, items))
            (DATA / f"{key}_{name}.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
            print(key, name, len(rows), "실패", sum(r["views"] is None for r in rows))


def _day(d):
    m = re.search(r"(\d{4})\. (\d+)\. (\d+)\.", d)
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def load(key):
    full = [x for x in json.loads((DATA / f"{key}_full.json").read_text(encoding="utf-8")) if _day(x["date"]) and _day(x["date"]) <= CUTOFF]
    songs = [x for x in json.loads((DATA / f"{key}_songs.json").read_text(encoding="utf-8")) if _day(x["date"]) and _day(x["date"]) <= CUTOFF]
    ids = {x["id"] for x in songs}
    videos = [x for x in full if x["id"] not in ids and not NOT_VIDEO.search(unicodedata.normalize("NFKC", x["title"]))]
    return videos, songs


def man(v):
    return f"{round(v / 1e4):,}만"


def _avg(rows):
    return st.mean(x["views"] for x in rows) if rows else 0


def stats(key):
    videos, songs = load(key)
    for name, rows in (("영상(노래 제외)", videos), ("일반 영상", [x for x in videos if x["shorts"] != 1]),
                       ("쇼츠", [x for x in videos if x["shorts"] == 1]), ("노래", songs)):
        print(f"\n{name} {len(rows)}개  평균 {man(_avg(rows))}")
        for x in sorted(rows, key=lambda x: -x["views"])[:5]:
            print(f"  {man(x['views']):>7} {x['date'][-13:]} {x.get('kind', '')} {x['title'][:70]}")


def summary():
    print("멤버 | 영상 평균 | 일반 평균 | 쇼츠 평균 | 최근1년 | 쇼츠 최고 | 일반 최고 | 곡 | 노래 평균 | 노래 최고")
    for key, name in MEMBERS:
        v, s = load(key)
        reg, sh = [x for x in v if x["shorts"] != 1], [x for x in v if x["shorts"] == 1]
        top = lambda rows: max(rows, key=lambda x: x["views"])
        rec = [x for x in v if _day(x["date"]) >= RECENT_FROM]
        print(" | ".join([name, man(_avg(v)), man(_avg(reg)), man(_avg(sh)), man(_avg(rec)),
                          f"{man(top(sh)['views'])} {top(sh)['title'][:30]}", f"{man(top(reg)['views'])} {top(reg)['title'][:30]}",
                          str(len(s)), man(_avg(s)), f"{man(top(s)['views'])} {top(s)['title'][:20]}"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("key"); f.add_argument("channel_id"); f.add_argument("song_key", nargs="?")
    f.add_argument("--app", default=str(Path(__file__).resolve().parents[3] / "Stel-Database" / "app.js"))
    sub.add_parser("stats").add_argument("key")
    sub.add_parser("summary")
    a = ap.parse_args()
    if a.cmd == "fetch":
        fetch(a.key, a.channel_id, a.song_key or a.key, a.app)
    elif a.cmd == "stats":
        stats(a.key)
    else:
        summary()
