"use client";

import { useEffect, useState } from "react";
import { GetWorkersStats } from "@/services/celery_utils/GetWorkerStats";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslations } from "next-intl";

const WorkersPage = () => {
    const [workerStats, setWorkerStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const t = useTranslations("Workers");

    useEffect(() => {
        const fetchWorkerStats = async () => {
            try {
                const stats = await GetWorkersStats();
                setWorkerStats(stats);
            } catch (err) {
                console.error("Error fetching worker statistics:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchWorkerStats();
    }, []);

    if (loading) {
        // Show skeletons for cards
        return (
            <div className="p-4">
                <h1 className="text-2xl font-bold mb-4 text-center">{t("title")}</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(3)].map((_, idx) => (
                        <Card key={idx} className="w-full">
                            <CardHeader>
                                <Skeleton className="h-6 w-1/2 mb-2" />
                                <Skeleton className="h-4 w-3/4" />
                            </CardHeader>
                            <CardContent>
                                <Skeleton className="h-4 w-1/2 mb-2" />
                                <Skeleton className="h-5 w-1/3 mb-2" />
                                <Skeleton className="h-4 w-2/3 mb-2" />
                                <Skeleton className="h-4 w-1/2 mb-2" />
                                <Skeleton className="h-4 w-1/3 mb-2" />
                                <Skeleton className="h-4 w-1/4 mb-2" />
                                <Skeleton className="h-4 w-1/2 mb-2" />
                                <Skeleton className="h-4 w-1/3 mb-2" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }


    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">{t("title")}</h1>
            {workerStats ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(workerStats).map(([workerName, stats]: any) => (
                        <Card key={workerName} className="w-full">
                            <CardHeader>
                                <CardTitle>{workerName}</CardTitle>
                                <CardDescription>
                                    {t("pid")}: {stats.pid} | {t("uptime")}: {stats.uptime} {t("seconds")}
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p><strong>{t("totalTasks")}:</strong> {stats.total["tasks.run_training"]}</p>
                                <h3 className="text-xl font-bold mt-4 mb-2">{t("pool")}</h3>
                                <p><strong>{t("implementation")}:</strong> {stats.pool.implementation}</p>
                                <p><strong>{t("maxConcurrency")}:</strong> {stats.pool["max-concurrency"]}</p>
                                <p><strong>{t("processes")}:</strong> {stats.pool.processes.join(", ")}</p>
                                <h3 className="text-xl font-bold mt-4 mb-2">{t("broker")}</h3>
                                <p><strong>{t("hostname")}:</strong> {stats.broker.hostname}</p>
                                <p><strong>{t("userid")}:</strong> {stats.broker.userid}</p>
                                <p><strong>{t("port")}:</strong> {stats.broker.port}</p>
                                <h3 className="text-xl font-bold mt-4 mb-2">{t("resourceUsage")}</h3>
                                <p><strong>{t("userTime")}:</strong> {stats.rusage.utime} {t("seconds")}</p>
                                <p><strong>{t("systemTime")}:</strong> {stats.rusage.stime} {t("seconds")}</p>
                                <p><strong>{t("maxRss")}:</strong> {stats.rusage.maxrss} KB</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : (
                <p>{t("noStats")}</p>
            )}
        </div>
    );
};

export default WorkersPage;