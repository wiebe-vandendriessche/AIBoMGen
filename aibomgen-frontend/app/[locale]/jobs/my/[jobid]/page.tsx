"use client";

import React, { useEffect, useState } from "react";
import { useIsAuthenticated } from "@azure/msal-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { GetMyTask } from "@/services/celery_utils/GetMyTask";
import { useMsal } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { Skeleton } from "@/components/ui/skeleton";
import { GetJobArtifacts } from "@/services/developer/GetJobArtifacts";
import { DownloadArtifact } from "@/services/developer/DownloadArtifact";
import { Button } from "@/components/ui/button"; // If you have a Button component
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Clipboard } from "lucide-react";
import { Tooltip, TooltipProvider, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { toast } from "sonner";
import { useTranslations } from "next-intl";

const JobDetailsPage = ({ params }: { params: Promise<{ locale: string; jobid: string }> }) => {
    const [jobid, setJobid] = useState<string | null>(null);
    const isAuthenticated = useIsAuthenticated();
    const [jobDetails, setJobDetails] = useState<any | null>(null);
    const { instance, inProgress } = useMsal();
    const [loading, setLoading] = useState<boolean>(true);
    const [artifactList, setArtifactList] = useState<string[]>([]);
    const [selectedArtifact, setSelectedArtifact] = useState<string>("");
    const [downloading, setDownloading] = useState<boolean>(false);
    const t = useTranslations("Jobs");

    // Unwrap the params Promise and set the jobid
    useEffect(() => {
        params.then((resolvedParams) => {
            setJobid(resolvedParams.jobid);
        });
    }, [params]);

    function getArtifactBasename(path: string) {
        return path.split("/").pop() || path;
    }

    // Fetch artifact list when jobid is available
    useEffect(() => {
        const fetchArtifacts = async () => {
            if (!jobid) return;
            try {
                const result = await GetJobArtifacts(instance, jobid);
                // result is { job_id, artifacts: [...] }
                if (result && Array.isArray(result.artifacts)) {
                    setArtifactList(result.artifacts);
                    setSelectedArtifact(result.artifacts[0] || "");
                }
            } catch (e) {
                setArtifactList([]);
            }
        };
        fetchArtifacts();
    }, [jobid, instance]);

    // Download handler
    const handleDownload = async () => {
        if (!selectedArtifact) return;
        setDownloading(true);
        try {
            // Only pass the basename to the backend
            const artifactBasename = getArtifactBasename(selectedArtifact);
            const response = await DownloadArtifact(instance, jobid!, artifactBasename + "?redirect=false");
            if (response && response.url) {
                window.open(response.url, "_blank");
                toast.success("Artifact download started!");
            }
        } catch (e) {
            toast.error("Failed to download artifact.");
        }
        setDownloading(false);
    };

    // Fetch job details for this jobid
    useEffect(() => {
        const fetchJobDetails = async () => {
            if (
                inProgress !== InteractionStatus.None ||
                !isAuthenticated ||
                !jobid
            ) {
                return;
            }
            setLoading(true);
            try {
                const data = await GetMyTask(instance, jobid);
                setJobDetails(data);
            } catch (error) {
                setJobDetails(null);
                console.error("Error fetching job details:", error);
            }
            setLoading(false);
        };

        fetchJobDetails();
    }, [jobid, instance, inProgress, isAuthenticated]);

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
                        <AlertTitle>{t("accessDenied")}</AlertTitle>
                        <AlertDescription>
                            {t("notLoggedIn")}
                        </AlertDescription>
                    </div>
                </Alert>
            </div>
        );
    }

    // Show a skeleton loader while loading or jobid is not yet resolved
    if (loading || !jobid) {
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

    // Show error if jobDetails is null (not found or error)
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

    // Render the job details
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
                    <CardTitle>{t("jobDetailsTitle")}</CardTitle>
                    <CardDescription>{t("jobDetailsDesc")}</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex items-center">
                            <strong>{t("id")}:</strong>
                            <span className="ml-2">{jobDetails.id}</span>
                            <span className="ml-6">
                                <TooltipProvider>
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={() => {
                                                    navigator.clipboard.writeText(jobDetails.id);
                                                    toast.success(t("copiedJobId"));
                                                }}
                                            >
                                                <Clipboard className="h-4 w-4" />
                                            </Button>
                                        </TooltipTrigger>
                                        <TooltipContent>
                                            {t("copyJobId")}
                                        </TooltipContent>
                                    </Tooltip>
                                </TooltipProvider>
                            </span>
                        </div>
                        <div>
                            <strong>{t("state")}:</strong> {jobDetails.state}
                        </div>
                        <div>
                            <strong>{t("worker")}:</strong> {jobDetails.worker || t("na")}
                        </div>
                        <div>
                            <strong>{t("trainingStatus")}:</strong> {jobDetails.result?.training_status || t("na")}
                        </div>
                        <div>
                            <strong>{t("uniqueDirectory")}:</strong> {jobDetails.result?.unique_dir || uniqueDir || t("na")}
                        </div>
                        <div>
                            <strong>{t("dateDone")}:</strong> {jobDetails.date_done ? new Date(jobDetails.date_done).toLocaleString() + " UTC" : t("na")}
                        </div>
                        <div>
                            <strong>{t("message")}:</strong> {jobDetails.result?.message || jobDetails.info?.message || t("na")}
                        </div>
                        <div>
                            <strong>{t("error")}:</strong> {jobDetails.result?.error || t("na")}
                        </div>
                        <hr />
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
                        <div className="flex items-center space-x-4">
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button
                                        variant="outline"
                                        className="min-w-[180px] justify-between"
                                        disabled={artifactList.length === 0}
                                    >
                                        {selectedArtifact
                                            ? getArtifactBasename(selectedArtifact)
                                            : t("selectArtifact")}
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                    <DropdownMenuLabel>{t("selectArtifact")}</DropdownMenuLabel>
                                    {artifactList.length === 0 && (
                                        <DropdownMenuItem disabled>{t("noArtifacts")}</DropdownMenuItem>
                                    )}
                                    {artifactList.map((name) => (
                                        <DropdownMenuItem
                                            key={name}
                                            onSelect={() => setSelectedArtifact(name)}
                                        >
                                            {getArtifactBasename(name)}
                                        </DropdownMenuItem>
                                    ))}
                                </DropdownMenuContent>
                            </DropdownMenu>
                            <Button
                                onClick={handleDownload}
                                disabled={!selectedArtifact || downloading}
                            >
                                {downloading ? t("downloading") : t("download")}
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default JobDetailsPage;