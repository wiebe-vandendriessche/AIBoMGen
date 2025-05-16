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

    function extractModelInfo(args: any[]) {
        if (!Array.isArray(args) || args.length < 6) return {};
        const [uniqueDir, modelUrl, datasetUrl, definitionUrl, modelInfo, trainingParams] = args;
        return { uniqueDir, modelUrl, datasetUrl, definitionUrl, modelInfo, trainingParams };
    }



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
    const {
        uniqueDir,
        modelUrl,
        datasetUrl,
        definitionUrl,
        modelInfo,
        trainingParams,
    } = extractModelInfo(jobDetails.args);

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
                            <strong>Worker:</strong> {jobDetails.worker || "N/A"}
                        </div>
                        <div>
                            <strong>Training Status:</strong> {jobDetails.result?.training_status || "N/A"}
                        </div>
                        <div>
                            <strong>Unique Directory:</strong> {jobDetails.result?.unique_dir || uniqueDir || "N/A"}
                        </div>
                        <div>
                            <strong>Date Done:</strong> {jobDetails.date_done ? new Date(jobDetails.date_done).toLocaleString() + " UTC" : "N/A"}
                        </div>
                        <div>
                            <strong>Message:</strong> {jobDetails.result?.message || jobDetails.info?.message || "N/A"}
                        </div>
                        <div>
                            <strong>Error:</strong> {jobDetails.result?.error || "N/A"}
                        </div>
                        <hr />
                        <div>
                            <strong>Model Info:</strong>
                            <ul className="ml-4">
                                <li><strong>Name:</strong> {modelInfo?.model_name || "N/A"}</li>
                                <li><strong>Framework:</strong> {modelInfo?.framework || "N/A"}</li>
                                <li><strong>Description:</strong> {modelInfo?.model_description || "N/A"}</li>
                                <li><strong>Author:</strong> {modelInfo?.author || "N/A"}</li>
                                <li><strong>Version:</strong> {modelInfo?.model_version || "N/A"}</li>
                                <li><strong>Type:</strong> {modelInfo?.model_type || "N/A"}</li>
                                <li><strong>Base Model:</strong> {modelInfo?.base_model || "N/A"}</li>
                                <li><strong>Base Model Source:</strong> {modelInfo?.base_model_source || "N/A"}</li>
                                <li><strong>Intended Use:</strong> {modelInfo?.intended_use || "N/A"}</li>
                                <li><strong>Out of Scope:</strong> {modelInfo?.out_of_scope || "N/A"}</li>
                                <li><strong>Misuse or Malicious:</strong> {modelInfo?.misuse_or_malicious || "N/A"}</li>
                                <li><strong>License:</strong> {modelInfo?.license_name || "N/A"}</li>
                            </ul>
                        </div>
                        <div>
                            <strong>Training Parameters:</strong>
                            <ul className="ml-4">
                                <li><strong>Epochs:</strong> {trainingParams?.epochs ?? "N/A"}</li>
                                <li><strong>Batch Size:</strong> {trainingParams?.batch_size ?? "N/A"}</li>
                                <li><strong>Validation Split:</strong> {trainingParams?.validation_split ?? "N/A"}</li>
                                <li><strong>Initial Epoch:</strong> {trainingParams?.initial_epoch ?? "N/A"}</li>
                                <li><strong>Steps per Epoch:</strong> {trainingParams?.steps_per_epoch ?? "N/A"}</li>
                                <li><strong>Validation Steps:</strong> {trainingParams?.validation_steps ?? "N/A"}</li>
                                <li><strong>Validation Freq:</strong> {trainingParams?.validation_freq ?? "N/A"}</li>
                            </ul>
                        </div>
                        <div>
                            <strong>Artifacts:</strong>
                            <ul className="ml-4">
                                <li>
                                    <strong>Model URL:</strong><br />
                                    <a href={modelUrl} className="underline" target="_blank" rel="noopener noreferrer">
                                        {modelUrl || "N/A"}
                                    </a>
                                </li>
                                <li>
                                    <strong>Dataset URL:</strong><br />
                                    <a href={datasetUrl} className="underline" target="_blank" rel="noopener noreferrer">
                                        {datasetUrl || "N/A"}
                                    </a>
                                </li>
                                <li>
                                    <strong>Definition URL:</strong><br />
                                    <a href={definitionUrl} className="underline" target="_blank" rel="noopener noreferrer">
                                        {definitionUrl || "N/A"}
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default JobDetailsPage;