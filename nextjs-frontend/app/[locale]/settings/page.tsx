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
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import LocaleSwitcher from "@/components/LocaleSwitcher";

const Settings = () => {
  const { theme, setTheme } = useTheme();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  return (
    <div className="p-4 flex justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Manage your application preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mt-4">
            <h2 className="text-lg font-semibold mb-2">Theme</h2>
            {/* THEME SELECT */}
            <Select onValueChange={(value) => setTheme(value)} value={theme}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Theme" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
                <SelectItem value="system">System</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-2">Language</h2>
            {/* LANGUAGE SELECT */}
            <LocaleSwitcher/>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;