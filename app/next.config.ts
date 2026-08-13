import type { NextConfig } from "next";

// GitHub Pages 배포 시 저장소 이름을 basePath로 넣는다 (예: /repo-name).
// 로컬 개발에서는 비워 둔다.
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig: NextConfig = {
  output: "export",
  basePath,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
