"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { GetMyRunningTask } from "@/services/celery_utils/GetMyRunningTask";
import { useMsal } from "@azure/msal-react";
import { useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";

export default function RunningJobPage() {
  const router = useRouter();
  const { jobid } = useParams();
  const [jobDetails, setJobDetails] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { instance, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const firstLoad = useRef(true);

  // Poll for running job details every 5 seconds
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;
    let cancelled = false;

    const fetchJobDetails = async () => {
      if (
        inProgress !== InteractionStatus.None ||
        !isAuthenticated ||
        !jobid
      ) {
        return;
      }
      // Only show skeleton on first load
      if (firstLoad.current) setIsLoading(true);
      try {
        const data = await GetMyRunningTask(instance, jobid as string);
        if (data?.error === "Task is not currently running.") {
          router.replace(`/jobs/my/${jobid}`);
          return;
        }
        if (!cancelled) setJobDetails(data);
      } catch (error) {
        if (!cancelled) setJobDetails(null);
        console.error("Error fetching running job details:", error);
      }
      if (!cancelled) setIsLoading(false);
      firstLoad.current = false;
    };

    fetchJobDetails();
    interval = setInterval(fetchJobDetails, 5000);

    return () => {
      cancelled = true;
      if (interval) clearInterval(interval);
    };
  }, [jobid, instance, inProgress, isAuthenticated, router]);

  function extractModelInfo(args: any[]) {
    if (!Array.isArray(args) || args.length < 6) return {};
    const [uniqueDir, modelUrl, datasetUrl, definitionUrl, modelInfo, trainingParams] = args;
    return { uniqueDir, modelUrl, datasetUrl, definitionUrl, modelInfo, trainingParams };
  }

  if (!isAuthenticated) {
    return (
      <div className="p-6 flex justify-center">
        <Alert className="max-w-xl w-full border-red-400" variant="destructive">
          <AlertCircle className="h-6 w-6" />
          <div>
            <AlertTitle>Access Denied</AlertTitle>
            <AlertDescription>
              You are not logged in. Please log in to access running job details.
            </AlertDescription>
          </div>
        </Alert>
      </div>
    );
  }

  if (isLoading || !jobid) {
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

  if (!jobDetails || jobDetails.error) {
    return (
      <div className="p-6 flex justify-center">
        <Alert className="max-w-xl w-full border-red-400" variant="destructive">
          <AlertCircle className="h-6 w-6" />
          <div>
            <AlertTitle>Job Not Found</AlertTitle>
            <AlertDescription>
              {jobDetails?.error || "This running job could not be found or you do not have access."}
            </AlertDescription>
          </div>
        </Alert>
      </div>
    );
  }

  const {
    uniqueDir,
    modelUrl,
    datasetUrl,
    definitionUrl,
    modelInfo,
    trainingParams,
  } = extractModelInfo(jobDetails.args);

  return (
    <div className="p-4 flex justify-center overflow-x-clip">
      <Card className="w-full max-w-xl">
        <CardHeader>
          <div className="flex items-center gap-2">
            <CardTitle>Running Job</CardTitle>
            <Loader2 className="animate-spin text-accent-foreground" />
          </div>
          <CardDescription>Details of the running job</CardDescription>
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
              <strong>Unique Directory:</strong> {uniqueDir || "N/A"}
            </div>
            <div>
              <strong>Time Started:</strong> {jobDetails.time_start ? new Date(jobDetails.time_start * 1000).toLocaleString() + " UTC" : "N/A"}
            </div>
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
}