import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // 開發模式：不強制 auth（key 檢查在 client 端）
  return NextResponse.next();
}

export const config = {
  matcher: "/admin/:path*",
};
