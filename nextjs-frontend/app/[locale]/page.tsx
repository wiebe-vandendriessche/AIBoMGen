import AppBarChart from "@/components/AppBarChart";
import CustomButton from "@/components/CustomButton";
import { Button } from "@/components/ui/button";
import { Divide } from "lucide-react";
import Image from "next/image";
import { useTranslations } from 'next-intl';
import { Link } from "@/i18n/navigation";

export default function Home() {
  const t = useTranslations('HomePage');
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-4 gap-4">
      <div className="bg-primary-foreground p-4 rounded-lg lg:col-span-2 xl:col-span-1 2xl:col-span-2">
        <AppBarChart />
      </div>
      <div className="bg-primary-foreground p-4 rounded-lg">{t("test")}</div>
      <div className="bg-primary-foreground p-4 rounded-lg">{t("test")}</div>
      <div className="bg-primary-foreground p-4 rounded-lg">{t("test")}</div>
      <div className="bg-primary-foreground p-4 rounded-lg lg:col-span-2">{t("test")}</div>
      <div className="bg-primary-foreground p-4 rounded-lg">{t("test")}</div>
      <div>
        <h1>{t("title")}</h1>
        <span>{t("about")}</span>
      </div>
    </div>
  );
}
