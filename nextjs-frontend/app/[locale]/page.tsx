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

export default function Home() {
  const t = useTranslations('HomePage');
  return (
    <div className="overflow-x-hidden">
      <HeroSection />
      <Features />
    </div>
  );
}
