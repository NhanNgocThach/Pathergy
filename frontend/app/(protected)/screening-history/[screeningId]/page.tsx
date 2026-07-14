import type { Metadata } from "next";
import { ScreeningHistoryDetail } from "@/features/screening/screening-history-detail";
export const metadata: Metadata = { title: "Screening history detail" };
export default async function ScreeningDetailPage({ params }: { params: Promise<{ screeningId: string }> }) { const { screeningId } = await params; return <ScreeningHistoryDetail screeningId={Number(screeningId)} />; }
