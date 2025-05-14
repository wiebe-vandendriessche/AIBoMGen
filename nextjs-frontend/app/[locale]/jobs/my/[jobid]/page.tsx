"use client";

import React, { useEffect, useState } from "react";
import { useJobContext } from "@/components/context/JobContext";
import { useIsAuthenticated } from "@azure/msal-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { GetMyTasks } from "@/services/celery_utils/GetMyTasks";
import { useMsal } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { Skeleton } from "@/components/ui/skeleton";

const JobDetailsPage = ({ params }: { params: Promise<{ locale: string; jobid: string }> }) => {
    const [jobid, setJobid] = useState<string | null>(null); // State to store the unwrapped jobid
    const { jobs, setJobs } = useJobContext(); // Access the jobs data from the context
    const isAuthenticated = useIsAuthenticated(); // Check if the user is authenticated
    const [jobDetails, setJobDetails] = useState<any | null>(null); // State to store the job details
    const { instance, inProgress } = useMsal(); // MSAL instance for fetching jobs

    // Unwrap the params Promise and set the jobid
    useEffect(() => {
        params.then((resolvedParams) => {
            setJobid(resolvedParams.jobid);
        });
    }, [params]);

    // Fetch jobs if the jobs array is empty
    useEffect(() => {
        const fetchJobs = async () => {
            if (inProgress !== InteractionStatus.None || !isAuthenticated) {
                return; // Wait for MSAL to finish initializing and ensure the user is authenticated
            }

            try {
                const data = await GetMyTasks(instance);
                setJobs(data); // Store the fetched jobs in the context
            } catch (error) {
                console.error("Error fetching jobs:", error);
            }
        };

        if (jobs.length === 0) {
            fetchJobs(); // Refetch jobs if the array is empty
        }
    }, [jobs, instance, inProgress, isAuthenticated, setJobs]);

    // Find the job details once the jobid and jobs are available
    useEffect(() => {
        if (jobid && jobs.length > 0) {
            const foundJob = jobs.find((job) => job.id === jobid);
            setJobDetails(foundJob || null);
        }
    }, [jobid, jobs]);


    // Redirect or show an error if the user is not authenticated
    if (!isAuthenticated) {
        return (
            <div className="p-6 flex justify-center">
                <Alert className="max-w-xl w-full border-red-400" variant="destructive">
                    <AlertCircle className="h-6 w-6" />
                    <div>
                        <AlertTitle>Access Denied</AlertTitle>
                        <AlertDescription>
                            You are not logged in. Please log in to access job details.
                        </AlertDescription>
                    </div>
                </Alert>
            </div>
        );
    }

    // Show a skeleton loader while the jobs array is empty
    if (jobs.length === 0) {
        return (
            <div className="p-4 flex justify-center overflow-x-clip">
                <Card className="w-full max-w-xl">
                    <CardHeader>
                        <CardTitle>
                            <Skeleton className="h-6 w-32" />
                        </CardTitle>
                        <CardDescription>
                            <Skeleton className="h-4 w-64" />
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Show a skeleton loader while the jobid or jobDetails is being resolved
    if (!jobid || !jobDetails) {
        return (
            <div className="p-4 flex justify-center overflow-x-clip">
                <Card className="w-full max-w-xl">
                    <CardHeader>
                        <CardTitle>
                            <Skeleton className="h-6 w-32" />
                        </CardTitle>
                        <CardDescription>
                            <Skeleton className="h-4 w-64" />
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                        </div>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Render the job details
    return (
        <div className="p-4 flex justify-center overflow-x-clip">
            <Card className="w-full max-w-xl">
                <CardHeader>
                    <CardTitle>Job Details</CardTitle>
                    <CardDescription>Details of the selected job</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div>
                            <strong>ID:</strong> {jobDetails.id}
                        </div>
                        <div>
                            <strong>State:</strong> {jobDetails.state}
                        </div>
                        <div>
                            <strong>Training Status:</strong> {jobDetails.result?.training_status || "N/A"}
                        </div>
                        <div>
                            <strong>Unique Directory:</strong> {jobDetails.result?.unique_dir || "N/A"}
                        </div>
                        <div>
                            <strong>Date Done:</strong> {jobDetails.date_done || "N/A"}
                        </div>
                        <div>
                            <strong>Error:</strong> {jobDetails.result?.error || "N/A"}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default JobDetailsPage;