"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import { useRouter } from "@/i18n/navigation";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { GetMyRunningTask } from "@/services/celery_utils/GetMyRunningTask";
import { useMsal } from "@azure/msal-react";
import { useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

export default function RunningJobPage() {
  const router = useRouter();
  const { jobid } = useParams();
  const [jobDetails, setJobDetails] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { instance, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const firstLoad = useRef(true);
  const t = useTranslations("Jobs");

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
      if (firstLoad.current) setIsLoading(true);
      try {
        const data = await GetMyRunningTask(instance, jobid as string);
        if (data?.error === "Task is not currently running.") {
          // Show toast before redirecting
          toast.success("Job finished!", {
            description: "The job has finished running. Redirecting to job details...",
            duration: 4000,
          });
          setTimeout(() => {
            router.replace(`/jobs/my/${jobid}`);
          }, 1500);
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
            <AlertTitle>{t("accessDenied")}</AlertTitle>
            <AlertDescription>
              {t("notLoggedInRunning")}
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
            <AlertTitle>{t("jobNotFound")}</AlertTitle>
            <AlertDescription>
              {jobDetails?.error || t("jobNotFoundDesc")}
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
            <CardTitle>{t("runningJobTitle")}</CardTitle>
            <Loader2 className="animate-spin text-accent-foreground" />
          </div>
          <CardDescription>{t("runningJobDesc")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <strong>{t("id")}:</strong> {jobDetails.id}
            </div>
            <div>
              <strong>{t("state")}:</strong> {jobDetails.state}
            </div>
            <div>
              <strong>{t("worker")}:</strong> {jobDetails.worker || t("na")}
            </div>
            <div>
              <strong>{t("uniqueDirectory")}:</strong> {uniqueDir || t("na")}
            </div>
            <div>
              <strong>{t("timeStarted")}:</strong> {jobDetails.time_start ? new Date(jobDetails.time_start * 1000).toLocaleString() + " UTC" : t("na")}
            </div>
            <div>
              <strong>{t("modelInfo")}:</strong>
              <ul className="ml-4">
                <li><strong>{t("modelName")}:</strong> {modelInfo?.model_name || t("na")}</li>
                <li><strong>{t("framework")}:</strong> {modelInfo?.framework || t("na")}</li>
                <li><strong>{t("modelDescription")}:</strong> {modelInfo?.model_description || t("na")}</li>
                <li><strong>{t("author")}:</strong> {modelInfo?.author || t("na")}</li>
                <li><strong>{t("modelVersion")}:</strong> {modelInfo?.model_version || t("na")}</li>
                <li><strong>{t("modelType")}:</strong> {modelInfo?.model_type || t("na")}</li>
                <li><strong>{t("baseModel")}:</strong> {modelInfo?.base_model || t("na")}</li>
                <li><strong>{t("baseModelSource")}:</strong> {modelInfo?.base_model_source || t("na")}</li>
                <li><strong>{t("intendedUse")}:</strong> {modelInfo?.intended_use || t("na")}</li>
                <li><strong>{t("outOfScope")}:</strong> {modelInfo?.out_of_scope || t("na")}</li>
                <li><strong>{t("misuseOrMalicious")}:</strong> {modelInfo?.misuse_or_malicious || t("na")}</li>
                <li><strong>{t("license")}:</strong> {modelInfo?.license_name || t("na")}</li>
              </ul>
            </div>
            <div>
              <strong>{t("trainingParameters")}:</strong>
              <ul className="ml-4">
                <li><strong>{t("epochs")}:</strong> {trainingParams?.epochs ?? t("na")}</li>
                <li><strong>{t("batchSize")}:</strong> {trainingParams?.batch_size ?? t("na")}</li>
                <li><strong>{t("validationSplit")}:</strong> {trainingParams?.validation_split ?? t("na")}</li>
                <li><strong>{t("initialEpoch")}:</strong> {trainingParams?.initial_epoch ?? t("na")}</li>
                <li><strong>{t("stepsPerEpoch")}:</strong> {trainingParams?.steps_per_epoch ?? t("na")}</li>
                <li><strong>{t("validationSteps")}:</strong> {trainingParams?.validation_steps ?? t("na")}</li>
                <li><strong>{t("validationFreq")}:</strong> {trainingParams?.validation_freq ?? t("na")}</li>
              </ul>
            </div>
            <div>
              <strong>{t("artifacts")}:</strong>
              <ul className="ml-4">
                <li>
                  <strong>{t("modelUrl")}:</strong><br />
                  <a href={modelUrl} className="underline" target="_blank" rel="noopener noreferrer">
                    {modelUrl || t("na")}
                  </a>
                </li>
                <li>
                  <strong>{t("datasetUrl")}:</strong><br />
                  <a href={datasetUrl} className="underline" target="_blank" rel="noopener noreferrer">
                    {datasetUrl || t("na")}
                  </a>
                </li>
                <li>
                  <strong>{t("definitionUrl")}:</strong><br />
                  <a href={definitionUrl} className="underline" target="_blank" rel="noopener noreferrer">
                    {definitionUrl || t("na")}
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