"use client";

import { Toaster } from "sonner";
import { useTheme } from "next-themes";

export default function ClientToaster() {
  const { resolvedTheme } = useTheme();

  // resolvedTheme is always "light" or "dark"
  return <Toaster theme={resolvedTheme === "dark" ? "dark" : "light"} />;
}