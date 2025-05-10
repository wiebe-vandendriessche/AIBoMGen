"use client";

import { LogOut, Moon, Settings, Sun, User } from "lucide-react";
import Link from "next/link";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Button } from "./ui/button";
import { useTheme } from "next-themes";
import { SidebarTrigger } from "./ui/sidebar";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "./configurations/msalConfig";
import { useState, useEffect } from "react";

const Navbar = () => {
    const { theme, setTheme } = useTheme();
    const { instance, accounts } = useMsal();

    const [user, setUser] = useState<{ name: string; picture: string }>({
        name: "Guest",
        picture: "https://ui-avatars.com/api/?name=g&background=random", // Default guest profile picture
    });

    // Update user state when accounts change
    useEffect(() => {
        if (accounts.length > 0) {
            const account = accounts[0];
            setUser({
                name: account.name || "Guest",
                picture: `https://ui-avatars.com/api/?name=${account.name}&background=random`, // Fallback avatar
            });
        } else {
            setUser({
                name: "Guest",
                picture: "https://ui-avatars.com/api/?name=g&background=random", // Reset to guest profile picture
            });
        }
    }, [accounts]);

    // Handle login
    const handleLogin = async () => {
        try {
            const loginResponse = await instance.loginPopup(loginRequest);
            const account = loginResponse.account;
            if (account) {
                instance.setActiveAccount(account); // Set the active account after login
                setUser({
                    name: account.name || "Guest",
                    picture: `https://ui-avatars.com/api/?name=${account.name}&background=random`,
                });
            }
        } catch (error) {
            console.error("Login failed:", error);
        }
    };

    // Handle logout
    const handleLogout = async () => {
        try {
            await instance.logoutPopup();
            instance.setActiveAccount(null); // Clear the active account after logout
            setUser({
                name: "Guest",
                picture: "https://ui-avatars.com/api/?name=g&background=random", // Reset to guest profile picture
            });
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    // Test the fetch job status endpoint
    const testJobStatus = async () => {
        try {
            const activeAccount = instance.getActiveAccount();
            if (!activeAccount) {
                console.error("No active account found. Please log in.");
                return;
            }

            // Acquire token silently using the scope defined in msalConfig
            const tokenResponse = await instance.acquireTokenSilent({
                ...loginRequest, // Use the loginRequest object from msalConfig
                account: activeAccount,
            });

            const accessToken = tokenResponse.accessToken;

            // Call the job status endpoint with a non-existing job ID
            const response = await fetch("http://localhost:8000/job_status/123e4567-e89b-12d3-a456-426614174000", {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Job status response:", data);
            } else {
                const errorData = await response.json();
                console.error("Error fetching job status:", errorData);
            }
        } catch (error) {
            console.error("Error testing job status endpoint:", error);
        }
    };



    return (
        <nav className="p-4 flex items-center justify-between">
            {/* Left side of the navbar */}
            <SidebarTrigger />
            <div className="flex items-center gap-4">
                <Link href="/">Dashboard</Link>
                {/* THEME MENU */}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="outline" size="icon">
                            <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                            <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                            <span className="sr-only">Toggle theme</span>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setTheme("light")}>
                            Light
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setTheme("dark")}>
                            Dark
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setTheme("system")}>
                            System
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
                {/* USER MENU */}
                <DropdownMenu>
                    <DropdownMenuTrigger>
                        <Avatar>
                            <AvatarImage src={user.picture} />
                            <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
                        </Avatar>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent sideOffset={10}>
                        <DropdownMenuLabel>{user.name}</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>
                            <User className="h-[1.2rem] w-[1.2rem] mr-2" />
                            Profile
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                            <Settings className="h-[1.2rem] w-[1.2rem] mr-2" />
                            Settings
                        </DropdownMenuItem>
                        <DropdownMenuItem variant="destructive" onClick={handleLogout}>
                            <LogOut className="h-[1.2rem] w-[1.2rem] mr-2" />
                            Logout
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
                {/* LOGIN BUTTON */}
                {user.name === "Guest" && (
                    <Button onClick={handleLogin}>Login</Button>
                )}
                {/* TEST JOB STATUS BUTTON */}
                <Button onClick={testJobStatus} variant="outline">
                    Test Job Status
                </Button>
            </div>
        </nav>
    );
};

export default Navbar;