import Link from "next/link";
import Badge from "@/components/Badge";
import Card from "@/components/Card";
import Section from "@/components/Section";
import data08 from "@/data/08.json";
import type { Data08 } from "@/data/types";
import styles from "./page.module.css";

/**
 * 방법론 페이지 (FR-6, M4).
 *
 * 01~08 프로젝트 페이지는 `useSearchParams`(필터 상태)를 쓰기 때문에
 * `page.tsx` + `<Suspense>` + `*PageClient.tsx`("use client") 골격을 쓴다.
 * 이 페이지는 필터도, 다른 어떤 클라이언트 상태도 쓰지 않는 순수 정적
 * 콘텐츠라 그 골격이 애초에 필요 없다 — 그래서 순수 서버 컴포넌트 하나로
 * 끝낸다.
 *
 * 실측으로 확인한 이유도 있다: 콘텐츠 분량이 많은 이 페이지를 굳이
 * `<Suspense>`로 감쌌더니, 이 Next.js 16.3 + Turbopack 조합의 스트리밍
 * 리빌(`$RC(...)`) 처리가 특정 크기 이상에서 멈춰버렸다(인시던트 카드를
 * 4개 그룹 이상 렌더링하면 재현 — 내용과 무관한 순수 구조 문제였고, 서버
 * 렌더링 자체는 항상 정상 완료됐다. `<Suspense>` 제거로 해결). 필요 없는
 * `<Suspense>`를 걷어내는 쪽이 이 프레임워크 버전에서는 더 안전하다.
 */

const data = data08 as Data08;

type BadgeTone = "neutral" | "primary" | "positive" | "cautionary" | "negative";

type Incident = {
  id: string;
  title: string;
  tag: { label: string; tone: BadgeTone };
  what: string;
  detected: string;
  action: string;
  source: string;
  link?: { href: string; label: string };
  followUp?: string;
};

type IncidentGroup = {
  eyebrow: string;
  title: string;
  description: string;
  incidents: Incident[];
};

// 8건 모두 이 프로젝트를 만들면서 실제로 부딪힌 것들이다. 지어낸 사례나
// 일반론이 아니다 — 각 카드의 "출처"가 실제 코드/문서 경로를 가리킨다.
const INCIDENT_GROUPS: IncidentGroup[] = [
  {
    eyebrow: "Live data",
    title: "실시간 데이터의 함정",
    description: "10분 간격으로 직접 찍는 프로젝트 8(동시시청자)에서 나온 두 가지 문제.",
    incidents: [
      {
        id: "01",
        title: "치지직 stale viewer 함정",
        tag: { label: "데이터 함정", tone: "negative" },
        what:
          "치지직 라이브 상태 API는 방송이 꺼진 상태(status: CLOSE)에서도 concurrentUserCount·" +
          "accumulateCount·liveTitle에 직전 방송의 값을 그대로 돌려준다. status 필드를 확인하지 " +
          "않으면 지금 방송 중인지 아닌지 구분할 수 없다.",
        detected:
          "첫 수집에서 11채널 전부 status: CLOSE인데 동시시청자가 1,600~3,800명으로 찍혔다. " +
          "방송 중이 아닌데 시청자가 있다는 모순으로 발견했다.",
        action:
          "common/chzzk.py의 normalize_live_status()에서 is_live가 False면 라이브 지표(동시시청자·" +
          "누적·방송 제목)를 전부 None으로 비우고, 잔존값은 last_concurrent_users / last_live_title로 " +
          "분리해 시계열에 절대 들어가지 못하게 한다. 이 처리가 없었다면 오프라인 구간이 " +
          "\"시청자가 계속 있는 평지\"로 그려져 동시시청자 시계열 전체가 거짓이 됐을 것이다.",
        source: "common/chzzk.py (normalize_live_status), 08_live_viewership/README.md",
        link: { href: "/projects/08-live", label: "프로젝트 08 · 동시시청자" },
      },
      {
        id: "02",
        title: "세션 수 vs 스냅샷 행 수 혼동",
        tag: { label: "표기 오류 · 수정됨", tone: "cautionary" },
        what:
          "화면에 coverage.n_live_rows(라이브 상태로 관측된 스냅샷 '행' 수)를 \"관측 세션\"이라는 " +
          "라벨로 보여준 적이 있다. 방송 1건을 10분 간격으로 6번 찍으면 행은 6개지만 세션은 1건이다 " +
          "— 서로 다른 것을 재는 숫자다.",
        detected:
          "실측값으로 확인했다: 어느 시점 n_live_rows는 13이었지만, 실제로 재구성한 세션(sessions)은 " +
          "3건뿐이었다. FR-5 가드의 기준(세션 5건)은 세션 수를 봐야 하는데, 행 수(13)를 기준으로 " +
          "판단하면 가드가 실제보다 낙관적으로 작동한다 — 5건 기준을 넘은 것처럼 보이지만 실제로는 " +
          "3건이라 미달이다.",
        action:
          "types.ts의 n_live_rows 문서 주석, app/page.tsx, data/aggregate.ts, " +
          "08-live/LivePageClient.tsx 4곳에서 n_live_rows를 세션 수로 오용하던 표기를 " +
          "sessions.length로 바꾸고, 두 값이 다르다는 주석을 코드에 남겼다.",
        source: "app/src/data/types.ts (n_live_rows 문서 주석), 08-live/LivePageClient.tsx",
        link: { href: "/projects/08-live", label: "프로젝트 08 · 동시시청자" },
      },
    ],
  },
  {
    eyebrow: "Collection method",
    title: "수집 방법의 재현성",
    description: "\"같은 걸 다시 재면 같은 숫자가 나오는가\"를 실패했던 사례.",
    incidents: [
      {
        id: "03",
        title: "02 커버곡 수집 방식 교체 (2026-08-12)",
        tag: { label: "재현성 문제 · 교체됨", tone: "cautionary" },
        what:
          "원래는 멤버당 3개 쿼리로 search.list(order=\"relevance\")를 돌려 커버곡을 셌다. " +
          "이 API는 관련도 상위 40개 결과만 주므로, cover_count가 \"그 채널의 커버곡 전체\"가 " +
          "아니라 \"관련도 상위 40개 창에 들어온 커버곡\" 수였다.",
        detected:
          "같은 방식으로 재수집했더니 커버곡 수가 오히려 줄었다. 하나코 나나 34개 → 29개, " +
          "유즈하 리코 46개 → 45개. 영상이 삭제된 게 아니라 검색 랭킹이 흔들려 상위 40개 창 " +
          "밖으로 밀려난 것이었다. 같은 코드에 같은 채널인데 실행 시점만 다르면 답이 달라진다 " +
          "— 즉 이 지표는 시계열 비교에 쓸 수 없는 값이었다.",
        action:
          "업로드 재생목록(playlistItems)을 전량 열거하고 제목 정규식(cover|커버|歌ってみた 등)으로 " +
          "커버를 판정하는 방식으로 교체했다. 결과가 결정적(같은 입력 → 같은 출력)으로 바뀌었고, " +
          "비용은 11명×3쿼리×100 units = 3,300 units에서 페이지(50건)당 1 unit인 열거 방식 " +
          "약 173 units로 약 19배 줄었다. 비용이 낮아진 덕분에 자동 갱신 주기도 주 1회에서 " +
          "일 1회로 앞당길 수 있었다. 전량 열거로 다시 세어보니 \"줄어든 것처럼 보이던\" 멤버들이 " +
          "사실 가장 심하게 과소집계되고 있었다 — 유즈하 리코는 45~46개가 아니라 실제 58개였다. " +
          "커버곡을 많이 낸 멤버일수록 상위 40개 창에 다 들어가지 못해 더 많이 누락됐다. " +
          "cover_count는 이 변경(2026-08-12) 이전 값과 비교할 수 없다.",
        source:
          "02_cover_song_ranking/collect.py 모듈 docstring, data/_meta.json (method_changed_at), " +
          "_archive/2026-08-03_original (변경 전 스냅샷)",
        link: { href: "/projects/02-cover", label: "프로젝트 02 · 커버곡 랭킹" },
      },
    ],
  },
  {
    eyebrow: "Dead ends & trust",
    title: "인프라",
    description: "빌드·배포 과정에서 만난 인프라 문제.",
    incidents: [
      {
        id: "08",
        title: "정적 빌드는 HTTP 서빙이 필요하다",
        tag: { label: "인프라", tone: "neutral" },
        what:
          "Next.js output: \"export\" 빌드는 에셋을 /_next/static/... 같은 루트 기준 절대경로로 " +
          "참조한다. 빌드된 HTML 파일을 file://로 직접 열면 브라우저가 /를 파일시스템 루트로 " +
          "해석해 에셋을 못 찾는다.",
        detected: "정적 산출물을 로컬에서 열어보는 과정에서 확인했다.",
        action:
          "정적 산출물(app/out)은 반드시 HTTP 서버로 서빙하기로 하고, .claude/launch.json에 " +
          "http.server 기반 app-static 설정(포트 3100)을 등록해뒀다.",
        source: ".claude/launch.json (app-static 설정)",
      },
    ],
  },
];

export default function Page() {
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <p className={styles.eyebrow}>Methodology</p>
        <h1 className={styles.title}>방법론</h1>
        <p className={styles.subhead}>
          이 대시보드가 쓰는 데이터가 어디서 오고, 어디서 믿을 수 없어지는지를 그대로 적는다.
          표본이 편향된 곳은 편향됐다고, 셀 수 없는 건 셀 수 없다고 쓴다 — 감추는 것보다 아는
          상태로 쓰는 쪽이 더 신뢰할 수 있는 분석이다.
        </p>
      </header>

      <Section
        eyebrow="FR-5"
        title="커버리지 가드가 각주보다 나은 이유"
        description="프로젝트 8(동시시청자)에 적용된 규칙과, 왜 경고 문구 대신 화면 자체를 바꾸는 쪽을 택했는지."
      />
      <Card padding="lg" className={styles.guardCard}>
        <Badge tone={data.enough_coverage ? "positive" : "negative"}>
          {data.enough_coverage ? "가드 해제됨 — 커버리지 충분" : "가드 작동 중 — 커버리지 부족"}
        </Badge>
        <p className={styles.guardText}>
          동시시청자는 소급 수집이 불가능하다 — 지금부터 쌓이는 것만 관측할 수 있다. 그래서
          <strong> 관측 24시간 미만이거나 세션 5건 미만이면, 최고/평균 동시시청자·팬덤 밀도 같은
          결론성 지표를 화면에 아예 보여주지 않는다.</strong> 대신 지금까지 실제로 관측된 원시
          포인트만 &quot;미리보기&quot;로 표시한다. 팔로워 증감처럼 스냅샷 2개만 있어도 유효한
          지표는 커버리지와 무관하게 먼저 보여준다 — 가드는 지표 전체가 아니라 &quot;세션이
          쌓여야 의미가 생기는 지표&quot;에만 건다.
        </p>
        <p className={styles.guardText}>
          이 빌드 시점 실측값: 실관측 {data.coverage.observed_hours.toLocaleString("ko-KR")}시간 ·
          세션 {data.sessions.length.toLocaleString("ko-KR")}건 (기준 24시간 · 5세션) · 커버리지{" "}
          {Math.round(data.coverage.coverage_ratio * 100)}% · 최대 단절{" "}
          {data.coverage.largest_gap_hours.toLocaleString("ko-KR")}시간 —{" "}
          {data.enough_coverage
            ? "기준을 넘어 결론성 지표가 열려 있다."
            : "기준에 못 미쳐 프로젝트 08 페이지의 동시시청자 순위·차트가 잠겨 있다."}
        </p>
        <p className={styles.guardText}>
          <strong>가드가 각주보다 나은 이유</strong> — 각주는 읽는 사람이 건너뛸 수 있다. 특히
          차트가 그럴듯해 보이면 더 그렇다. &quot;표본이 얇습니다&quot;라는 문장 하나가 화려한
          막대그래프 옆에 작게 붙어 있어봤자 잘 읽히지 않는다. 가드는 반대로 동작한다 — 조건을
          만족하지 못하면 그 결론성 차트 자체가 애초에 렌더링되지 않는다. &quot;얇은 데이터로
          만든 그럴듯한 차트&quot;가 물리적으로 존재할 수 없게 만드는 쪽이, 옆에 경고를 붙이는
          쪽보다 훨씬 강한 보장이다.
        </p>
        <Link href="/projects/08-live" className={styles.guardLink}>
          프로젝트 08 · 동시시청자에서 실제 동작 확인 →
        </Link>
      </Card>

      {INCIDENT_GROUPS.map((group) => (
        <div key={group.title} className={styles.group}>
          <Section eyebrow={group.eyebrow} title={group.title} description={group.description} />
          <div className={styles.incidentList}>
            {group.incidents.map((incident) => (
              <Card key={incident.id} padding="lg" className={styles.incidentCard}>
                <div className={styles.incidentHeader}>
                  <span className={styles.incidentIndex}>{incident.id}</span>
                  <h3 className={styles.incidentTitle}>{incident.title}</h3>
                  <Badge tone={incident.tag.tone}>{incident.tag.label}</Badge>
                </div>

                <dl className={styles.incidentBody}>
                  <div className={styles.incidentField}>
                    <dt>무엇이 있었나</dt>
                    <dd>{incident.what}</dd>
                  </div>
                  <div className={styles.incidentField}>
                    <dt>어떻게 발견했나</dt>
                    <dd>{incident.detected}</dd>
                  </div>
                  <div className={styles.incidentField}>
                    <dt>어떻게 처리했나</dt>
                    <dd>{incident.action}</dd>
                  </div>
                </dl>

                {incident.followUp ? (
                  <div className={styles.followUp}>
                    <Badge tone="cautionary">진행 중인 후속 조사</Badge>
                    <p className={styles.followUpText}>{incident.followUp}</p>
                  </div>
                ) : null}

                <div className={styles.incidentFooter}>
                  <span className={styles.source}>출처 · {incident.source}</span>
                  {incident.link ? (
                    <Link href={incident.link.href} className={styles.incidentLink}>
                      {incident.link.label} →
                    </Link>
                  ) : null}
                </div>
              </Card>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
