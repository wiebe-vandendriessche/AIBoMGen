"use client"

import { BrainCircuit, Calendar, ChevronDown, ChevronUp, Cookie, GlobeLock, Home, Inbox, Plus, Projector, Search, Settings, User2 } from "lucide-react";
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
import { useLocalStorage } from "@/hooks/use-local";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { GetMyTasks } from "@/services/celery_utils/GetMyTasks";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
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
    const [isCollapsibleOpen, setIsCollapsibleOpen] = useLocalStorage("collapsibleState", false); // Use local storage to persist state
    const [isMounted, setIsMounted] = useState(false); // Track if the component is mounted
    const { instance } = useMsal();
    const isAuthenticated = useIsAuthenticated();
    const [jobs, setJobs] = useState([]);

    useEffect(() => {
        setIsMounted(true); // Set mounted state to true after the component mounts
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

    useEffect(() => {
        setIsMounted(true); // Set mounted state to true after the component mounts

        const fetchJobs = async () => {
            if (isAuthenticated) {
                try {
                    const data = await GetMyTasks(instance);
                    setJobs(data);
                } catch (error) {
                    console.error("Error fetching jobs:", error);
                }
            }
        };

        fetchJobs();
    }, [instance, isAuthenticated]);

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
    const { state, isMobile } = useSidebar(); // Get the sidebar state and isMobile flag

    return (
        <Sidebar
            collapsible="icon"
            className="fixed top-0 left-0 h-full w-64 bg-background z-30">
            <SidebarHeader className="py-4">
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton asChild>
                            <Link href="/">
                                <Image src="/logo.svg" alt="logo" width={30} height={30} className="" />
                                <span className="font-bold">{t("title")}</span>
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
                                        tooltip={t(item.title)} // Add tooltip
                                    >
                                        <Link href={item.url}>
                                            <item.icon />
                                            <span>{t(item.title)}</span>
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
                    <SidebarGroupAction className="w-6 h-6">
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Link
                                        href="/jobs/new"
                                        className="w-6 h-6 items-center justify-center flex"
                                    >
                                        <Plus className="w-4 h-4" />
                                        <span className="sr-only">{t("addJob")}</span>
                                    </Link>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p>{t("addJob")}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </SidebarGroupAction>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            <SidebarMenuItem>
                                <SidebarMenuButton
                                    asChild
                                    tooltip={t("seeAllJobs")}
                                >
                                    <Link href="/jobs/all">
                                        <Projector />
                                        <span>{t("seeAllJobs")}</span>
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <SidebarMenuButton
                                    asChild
                                    tooltip={t("seeMyJobs")} // Tooltip
                                >
                                    <Link href="/jobs/my">
                                        <Projector />
                                        <span>{t("seeMyJobs")}</span>
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                            {isMounted && isAuthenticated && ( // Ensure Collapsible renders only after mounting and user is authenticated
                                <Collapsible
                                    open={isCollapsibleOpen}
                                    onOpenChange={setIsCollapsibleOpen} // Update state on change
                                    className="group/collapsible"
                                >
                                    <SidebarMenuItem>
                                        <CollapsibleTrigger
                                            asChild
                                            className={state === "collapsed" && !isMobile ? "pointer-events-none opacity-50" : ""} // Allow toggling on mobile
                                        >
                                            <SidebarMenuButton>
                                                <BrainCircuit />
                                                <span>{t("recentJobs")}</span>
                                                <ChevronDown
                                                    className={`ml-auto transition-transform ${isCollapsibleOpen ? "rotate-180" : ""
                                                        }`}
                                                />
                                            </SidebarMenuButton>
                                        </CollapsibleTrigger>
                                        <CollapsibleContent>
                                            <SidebarMenuSub>
                                                {jobs
                                                    .filter((job: any) => job.date_done) // Ensure jobs with date_done are included
                                                    .sort((a: any, b: any) => new Date(b.date_done).getTime() - new Date(a.date_done).getTime()) // Sort by date_done descending
                                                    .slice(0, 5) // Take the most recent 5 jobs
                                                    .map((job: any) => (
                                                        <SidebarMenuSubItem key={job.id}>
                                                            <SidebarMenuSubButton asChild>
                                                                <Link href={`/jobs/my/${job.id}`}>
                                                                    <BrainCircuit />
                                                                    <span>{job.id}</span>
                                                                </Link>
                                                            </SidebarMenuSubButton>
                                                        </SidebarMenuSubItem>
                                                    ))}
                                            </SidebarMenuSub>
                                        </CollapsibleContent>
                                    </SidebarMenuItem>
                                </Collapsible>
                            )}
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
                                        <GlobeLock />
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
                                        <Cookie />
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