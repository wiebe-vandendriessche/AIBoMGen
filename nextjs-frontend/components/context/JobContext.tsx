"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

// Define the shape of the context
interface JobContextType {
  jobs: any[];
  setJobs: (jobs: any[]) => void;
}

// Create the context
const JobContext = createContext<JobContextType | undefined>(undefined);

// Provider component
export const JobProvider = ({ children }: { children: React.ReactNode }) => {
  const [jobs, setJobs] = useState<any[]>([]);

  // Log the jobs array whenever it changes
  useEffect(() => {
    console.log("Jobs context updated:", jobs);
  }, [jobs]);

  return (
    <JobContext.Provider value={{ jobs, setJobs }}>
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
