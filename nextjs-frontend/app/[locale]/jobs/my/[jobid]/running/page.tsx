"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function RunningJobPage() {
  const router = useRouter();
  const { jobid } = useParams(); // Extract the job ID from the URL
  const [jobDetails, setJobDetails] = useState<any | null>(null); // State to store the job details
  const [isLoading, setIsLoading] = useState(true); // Loading state

  // Mock job details (replace with actual data fetching logic)
  // TODO: new endpoint that inspect one running job by ID
  useEffect(() => {
    // Simulate fetching job details
    setTimeout(() => {
      setJobDetails({
        id: jobid,
        state: "Running",
        progress: 45, // Example progress percentage
        unique_dir: "11552122-b274-4940-b767-f6a18a933c8b",
        training_status: "Training in progress",
        date_started: "2025-05-15T10:00:00Z",
      });
      setIsLoading(false);
    }, 1000); // Simulate a 1-second delay
  }, [jobid]);

  // Show a skeleton loader while loading
  if (isLoading) {
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
          <CardTitle>Running Job</CardTitle>
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
              <strong>Training Status:</strong> {jobDetails.training_status}
            </div>
            <div>
              <strong>Unique Directory:</strong> {jobDetails.unique_dir}
            </div>
            <div>
              <strong>Date Started:</strong> {new Date(jobDetails.date_started).toLocaleString()}
            </div>
            <div>
              <strong>Progress:</strong>
              <div className="w-full bg-gray-200 rounded-full h-4 mt-2">
                <div
                  className="bg-blue-500 h-4 rounded-full"
                  style={{ width: `${jobDetails.progress}%` }}
                ></div>
              </div>
              <p className="mt-2 text-sm text-gray-600">{jobDetails.progress}% completed</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}