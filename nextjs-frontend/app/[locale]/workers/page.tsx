"use client";

import { useEffect, useState } from "react";
import { GetWorkersStats } from "@/services/celery_utils/GetWorkerStats";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";

const WorkersPage = () => {
    const [workerStats, setWorkerStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchWorkerStats = async () => {
            try {
                const stats = await GetWorkersStats();
                setWorkerStats(stats);
            } catch (err) {
                setError("Failed to fetch worker statistics.");
            } finally {
                setLoading(false);
            }
        };

        fetchWorkerStats();
    }, []);

    if (loading) {
        return <div>Loading worker statistics...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4 text-center">Worker Statistics</h1>
            {workerStats ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(workerStats).map(([workerName, stats]: any) => (
                        <Card key={workerName} className="w-full">
                            <CardHeader>
                                <CardTitle>{workerName}</CardTitle>
                                <CardDescription>PID: {stats.pid} | Uptime: {stats.uptime} seconds</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p><strong>Total Tasks:</strong> {stats.total["tasks.run_training"]}</p>
                                <h3 className="text-xl font-bold mt-4 mb-2">Pool</h3>
                                <p><strong>Implementation:</strong> {stats.pool.implementation}</p>
                                <p><strong>Max Concurrency:</strong> {stats.pool["max-concurrency"]}</p>
                                <p><strong>Processes:</strong> {stats.pool.processes.join(", ")}</p>
                                <h3 className="text-xl font-bold mt-4 mb-2">Broker</h3>
                                <p><strong>Hostname:</strong> {stats.broker.hostname}</p>
                                <p><strong>User ID:</strong> {stats.broker.userid}</p>
                                <p><strong>Port:</strong> {stats.broker.port}</p>
                                <h3 className="text-xl font-bold mt-4 mb-2">Resource Usage</h3>
                                <p><strong>User Time:</strong> {stats.rusage.utime} seconds</p>
                                <p><strong>System Time:</strong> {stats.rusage.stime} seconds</p>
                                <p><strong>Max RSS:</strong> {stats.rusage.maxrss} KB</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : (
                <p>No worker statistics available.</p>
            )}
        </div>
    );
};

export default WorkersPage;