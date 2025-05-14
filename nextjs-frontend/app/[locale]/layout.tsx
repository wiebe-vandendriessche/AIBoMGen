import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import App from "next/app";
import Navbar from "@/components/Navbar";
import AppSidebar from "@/components/AppSidebar";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import { SidebarProvider } from "@/components/ui/sidebar";
import { cookies } from "next/headers";
import MsalProviderWrapper from "@/components/providers/MsalProviderWrapper";
import { NextIntlClientProvider, hasLocale, useTranslations } from 'next-intl';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';


const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AIBoMGen: Dashboard",
  description: "AIBoMGen: tool for thrustworthy AI-generated BOMs",
  icons: {
    icon: "logo.svg",
  }
};


export default async function RootLayout({
  children,
  params
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}>) {

  const cookieStore = await cookies()
  const defaultOpen = cookieStore.get("sidebar_state")?.value === "true"

  // Ensure that the incoming `locale` is valid
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  const messages = (await import(`../../messages/${locale}.json`)).default;

  return (
    <html lang={locale} suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
        >
          <MsalProviderWrapper>
            <NextIntlClientProvider locale={locale} messages={messages}>
              <SidebarProvider defaultOpen={defaultOpen}>
                <AppSidebar />
                <main className="w-full">
                  <Navbar />
                  <div>
                    {children}
                  </div>
                </main>
              </SidebarProvider>
            </NextIntlClientProvider>
          </MsalProviderWrapper>
        </ThemeProvider>
      </body>
    </html>
  );
}
