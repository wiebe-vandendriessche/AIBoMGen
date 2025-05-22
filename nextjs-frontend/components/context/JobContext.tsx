"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

// Define the shape of the context
interface JobContextType {
  jobs: any[]; // My Jobs (authentication required)
  setJobs: (jobs: any[]) => void;
  allJobs: any[]; // All Jobs
  setAllJobs: (allJobs: any[]) => void;
}

// Create the context
const JobContext = createContext<JobContextType | undefined>(undefined);

// Provider component
export const JobProvider = ({ children }: { children: React.ReactNode }) => {
  const [jobs, setJobs] = useState<any[]>([]); // State for "My Jobs"
  const [allJobs, setAllJobs] = useState<any[]>([]); // State for "All Jobs"

  // Log the jobs array whenever it changes
  useEffect(() => {
    console.log("Jobs context updated:", jobs);
  }, [jobs]);

  return (
    <JobContext.Provider value={{ jobs, setJobs, allJobs, setAllJobs }}>
      {children}
    </JobContext.Provider>
  );
};

// Hook to use the context
export const useJobContext = () => {
  const context = useContext(JobContext);
  if (!context) {
    throw new Error("useJobContext must be used within a JobProvider");
  }
  return context;
};
