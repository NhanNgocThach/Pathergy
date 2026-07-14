import * as React from "react";
import { cn } from "@/lib/utils";

export function Table({ className, ...props }: React.ComponentProps<"table">) { return <div className="w-full overflow-x-auto"><table className={cn("w-full border-collapse text-left text-sm", className)} {...props} /></div>; }
export function TableHeader(props: React.ComponentProps<"thead">) { return <thead className="border-b bg-muted/60" {...props} />; }
export function TableBody(props: React.ComponentProps<"tbody">) { return <tbody className="divide-y" {...props} />; }
export function TableRow(props: React.ComponentProps<"tr">) { return <tr {...props} />; }
export function TableHead(props: React.ComponentProps<"th">) { return <th className="px-4 py-3 font-semibold" scope="col" {...props} />; }
export function TableCell(props: React.ComponentProps<"td">) { return <td className="px-4 py-3 align-top" {...props} />; }
