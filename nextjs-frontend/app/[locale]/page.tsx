import AppBarChart from "@/components/AppBarChart";
import CustomButton from "@/components/CustomButton";
import { Button } from "@/components/ui/button";
import { Divide } from "lucide-react";
import Image from "next/image";
import { useTranslations } from 'next-intl';
import { Link } from "@/i18n/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import HeroSection from "@/components/hero-section";
import Features from "@/components/features-2";
import { setRequestLocale } from "next-intl/server";
import { use } from "react";

export default function Home({params}: Readonly<{params: Promise<{locale: string}>}>) {
    const {locale} = use(params);
    // Enable static rendering
  setRequestLocale(locale);
  const t = useTranslations('HomePage');
  return (
      <div className="overflow-x-hidden">
        <HeroSection />
        <Features />
      </div>
  );
}
