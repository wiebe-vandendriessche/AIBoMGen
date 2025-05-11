"use client"

import { BrainCircuit, Calendar, ChevronDown, ChevronUp, Home, Inbox, Plus, Projector, Search, Settings, User2 } from "lucide-react";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupAction,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuBadge,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarMenuSub,
    SidebarMenuSubButton,
    SidebarMenuSubItem,
    SidebarSeparator,
} from "@/components/ui/sidebar"
import Link from "next/link";
import Image from "next/image";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { useTranslations } from "next-intl";
import { useSidebar } from "@/components/ui/sidebar";
import {
    Drawer,
    DrawerClose,
    DrawerContent,
    DrawerDescription,
    DrawerFooter,
    DrawerHeader,
    DrawerTitle,
    DrawerTrigger,
} from "@/components/ui/drawer";
import { Button } from "./ui/button";
import { setCookie, getCookie, deleteCookie } from "@/lib/cookies";
import { useEffect, useState } from "react";

const items = [
    { title: 'Home', url: '/', icon: Home },
    { title: 'Inbox', url: '#', icon: Inbox },
    { title: 'Calendar', url: '#', icon: Calendar },
    { title: 'Search', url: '#', icon: Search },
    { title: 'Settings', url: '#', icon: Settings },
]


const AppSidebar = () => {
    const [cookieConsent, setCookieConsent] = useState<string | null>(null);
    const [isCookieDrawerOpen, setIsCookieDrawerOpen] = useState(false); // State to control drawer visibility

    useEffect(() => {
        // Check if the user has already made a choice
        const consent = getCookie("cookieConsent");
        setCookieConsent(consent);

        // If no consent is found, show the drawer after 5 seconds
        if (!consent) {
            const timer = setTimeout(() => {
                setIsCookieDrawerOpen(true);
            }, 5000);

            return () => clearTimeout(timer); // Cleanup timer on unmount
        }
    }, []);

    const handleAcceptAll = () => {
        setCookie("cookieConsent", "accepted", 365); // Store consent for 1 year
        setCookieConsent("accepted");
        setIsCookieDrawerOpen(false); // Close the drawer
        console.log("All cookies accepted");
    };

    const handleRejectAll = () => {
        setCookie("cookieConsent", "rejected", 365); // Store rejection for 1 year
        // deleteCookie("analytics"); // Example: Remove analytics cookies
        // deleteCookie("marketing"); // Example: Remove marketing cookies
        setCookieConsent("rejected");
        setIsCookieDrawerOpen(false); // Close the drawer
        console.log("All cookies rejected");
    };

    const t = useTranslations("AppSidebar");
    const { state } = useSidebar(); // Get the sidebar state (expanded or collapsed)

    return (
        <Sidebar collapsible="icon">
            <SidebarHeader className="py-4">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton asChild>
                            <Link href="/">
                                <Image src="/logo.svg" alt="logo" width={30} height={30} className="" />
                                {state !== "collapsed" && <span className="font-bold">{t("title")}</span>}
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarHeader>

            <SidebarSeparator />

            <SidebarContent>
                <SidebarGroup>
                    <SidebarGroupLabel>{t("mainMenu")}</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            {items.map((item) => (
                                <SidebarMenuItem key={item.title}>
                                    <SidebarMenuButton
                                        asChild
                                        tooltip={state === "collapsed" ? t(item.title) : undefined} // Add tooltip only when collapsed
                                    >
                                        <Link href={item.url}>
                                            <item.icon />
                                            {state !== "collapsed" && <span>{t(item.title)}</span>}
                                        </Link>
                                    </SidebarMenuButton>
                                    {item.title === "Inbox" && (
                                        <SidebarMenuBadge>25</SidebarMenuBadge>
                                    )}
                                </SidebarMenuItem>
                            ))}
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
                <SidebarGroup>
                    <SidebarGroupLabel>{t("trainingJobs")}</SidebarGroupLabel>
                    <SidebarGroupAction>
                        <Plus /> <span className="sr-only">{t("addJob")}</span>
                    </SidebarGroupAction>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            <SidebarMenuItem>
                                <SidebarMenuButton
                                    asChild
                                    tooltip={state === "collapsed" ? t("seeAllJobs") : undefined} // Tooltip for collapsed state
                                >
                                    <Link href="/jobs/all">
                                        <Projector />
                                        {state !== "collapsed" && <span>{t("seeAllJobs")}</span>}
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <SidebarMenuButton
                                    asChild
                                    tooltip={state === "collapsed" ? t("seeMyJobs") : undefined} // Tooltip for collapsed state
                                >
                                    <Link href="/jobs/my">
                                        <Projector />
                                        {state !== "collapsed" && <span>{t("seeMyJobs")}</span>}
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                            <Collapsible defaultOpen className="group/collapsible">
                                <SidebarMenuItem>
                                    <CollapsibleTrigger
                                        asChild
                                        className={state === "collapsed" ? "pointer-events-none opacity-50" : ""}
                                    >
                                        <SidebarMenuButton>
                                            <BrainCircuit />
                                            {state !== "collapsed" && <span>{t("myJobs")}</span>}
                                            <ChevronDown
                                                className={`ml-auto transition-transform ${state === "collapsed" ? "hidden" : "group-data-[state=open]/collapsible:rotate-180"
                                                    }`}
                                            />
                                        </SidebarMenuButton>
                                    </CollapsibleTrigger>
                                    <CollapsibleContent>
                                        <SidebarMenuSub>
                                            <SidebarMenuSubItem>
                                                <SidebarMenuSubButton asChild>
                                                    <Link href="/jobs/1">
                                                        <BrainCircuit />
                                                        <span>{t("job1")}</span>
                                                    </Link>
                                                </SidebarMenuSubButton>
                                            </SidebarMenuSubItem>
                                            <SidebarMenuSubItem>
                                                <SidebarMenuSubButton asChild>
                                                    <Link href="/jobs/2">
                                                        <BrainCircuit />
                                                        <span>{t("job2")}</span>
                                                    </Link>
                                                </SidebarMenuSubButton>
                                            </SidebarMenuSubItem>
                                        </SidebarMenuSub>
                                    </CollapsibleContent>
                                </SidebarMenuItem>
                            </Collapsible>
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </SidebarContent>
            <SidebarFooter>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <Drawer>
                            <DrawerTrigger asChild>
                                <SidebarMenuButton asChild>
                                    <Link href="#">
                                        {t("privacyStatement")}
                                    </Link>
                                </SidebarMenuButton>
                            </DrawerTrigger>
                            <DrawerContent className="flex flex-col items-center justify-center text-center p-6">
                                <DrawerHeader>
                                    <DrawerTitle>{t("privacyTitle")}</DrawerTitle>
                                    <DrawerDescription>{t("privacyDescription")}</DrawerDescription>
                                </DrawerHeader>
                                <DrawerFooter>
                                </DrawerFooter>
                            </DrawerContent>
                        </Drawer>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                        <Drawer open={isCookieDrawerOpen} onOpenChange={setIsCookieDrawerOpen}>
                            <DrawerTrigger asChild>
                                <SidebarMenuButton asChild>
                                    <Link href="#">
                                        {t("cookieMenu")}
                                    </Link>
                                </SidebarMenuButton>
                            </DrawerTrigger>
                            <DrawerContent className="flex flex-col items-center justify-center text-center p-6">
                                <DrawerHeader>
                                    <DrawerTitle className="text-lg font-bold">{t("cookieTitle")}</DrawerTitle>
                                    <DrawerDescription className="text-sm text-muted-foreground">
                                        {t("cookieDescription")}
                                    </DrawerDescription>
                                </DrawerHeader>
                                <div className="p-4">
                                    <p className="mb-4">{t("cookieExplanation")}</p>
                                    <ul className="list-disc pl-6 text-left">
                                        <li>{t("essentialCookies")}</li>
                                        <li>{t("analyticsCookies")}</li>
                                        <li>{t("marketingCookies")}</li>
                                    </ul>
                                </div>
                                <DrawerFooter className="flex flex-col items-center gap-4 mt-4">
                                    <Button
                                        onClick={handleRejectAll}
                                        variant={"destructive"}
                                        className="w-40"
                                    >
                                        {t("rejectAll")}
                                    </Button>
                                    <Button
                                        onClick={handleAcceptAll}
                                        variant={"default"}
                                        className="w-40"
                                    >
                                        {t("acceptAll")}
                                    </Button>
                                </DrawerFooter>
                            </DrawerContent>
                        </Drawer>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    );
};

export default AppSidebar;