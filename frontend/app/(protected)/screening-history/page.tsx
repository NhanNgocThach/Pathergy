import type { Metadata } from "next";
import { ScreeningHistoryList } from "@/features/screening/screening-history-list";
export const metadata: Metadata = { title: "Screening History" };
export default function ScreeningHistoryPage() { return <ScreeningHistoryList />; }
