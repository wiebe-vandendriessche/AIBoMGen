"use client";

import { Toaster } from "sonner";
import { useTheme } from "next-themes";

export default function ClientToaster() {
  const { theme } = useTheme();

  // Map the theme to "light" or "dark" for Sonner
  const mappedTheme = theme === "dark" ? "dark" : "light";

  return <Toaster theme={mappedTheme} />;
}