"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import LocaleSwitcher from "@/components/LocaleSwitcher";
import { useTranslations } from "next-intl";

const Settings = () => {
  const { theme, setTheme } = useTheme();
  const [loading, setLoading] = useState(true);
  const t = useTranslations("Settings");

  return (
    <div className="p-4 flex justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{t("title")}</CardTitle>
          <CardDescription>{t("description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mt-4">
            <h2 className="text-lg font-semibold mb-2">{t("theme")}</h2>
            {/* THEME SELECT */}
            <Select onValueChange={(value) => setTheme(value)} value={theme}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder={t("theme")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">{t("light")}</SelectItem>
                <SelectItem value="dark">{t("dark")}</SelectItem>
                <SelectItem value="system">{t("system")}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">{t("language")}</h2>
            {/* LANGUAGE SELECT */}
            <LocaleSwitcher />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;