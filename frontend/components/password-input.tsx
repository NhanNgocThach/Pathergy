"use client";

import { Eye, EyeOff } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/i18n/i18n-provider";

export const PasswordInput = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(function PasswordInput(props, ref) {
  const { t } = useI18n();
  const [visible, setVisible] = React.useState(false);
  return <div className="relative"><Input ref={ref} type={visible ? "text" : "password"} className="pr-12" {...props} /><Button type="button" variant="ghost" size="icon" className="absolute right-0 top-0" aria-label={visible ? t("common.hidePassword") : t("common.showPassword")} onClick={() => setVisible((value) => !value)}>{visible ? <EyeOff className="size-5" aria-hidden="true" /> : <Eye className="size-5" aria-hidden="true" />}</Button></div>;
});
