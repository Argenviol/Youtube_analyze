/**
 * 프로젝트 id ↔ 제목/경로 매핑. 허브 카드 그리드는 자체 배열을 쓰지만(카드별
 * 부가 정보가 달라서), 드릴다운 패널·신선도 배지처럼 "이 프로젝트가 뭐였지"를
 * 되짚어야 하는 재사용 컴포넌트는 여기를 참조한다.
 */
import type { ProjectId } from "./types";

export const PROJECT_TITLE: Record<ProjectId, string> = {
  "01": "멤버 채널 성과",
  "02": "커버곡 랭킹",
  "03": "치지직 방송 패턴",
  "04": "키리누키 생태계",
  "05": "댓글 여론",
  "06": "경쟁사 비교",
  "08": "동시시청자",
};

export const PROJECT_HREF: Record<ProjectId, string> = {
  "01": "/projects/01-channel",
  "02": "/projects/02-cover",
  "03": "/projects/03-stream",
  "04": "/projects/04-kirinuki",
  "05": "/projects/05-sentiment",
  "06": "/projects/06-competitor",
  "08": "/projects/08-live",
};
