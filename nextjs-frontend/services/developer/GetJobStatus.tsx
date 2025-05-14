import { fetcher } from "../api"

export const GetJobStatus = async (instance: any, jobId: string) => {
    const endpoint = `/developer/job_status/${jobId}`;
    return await fetcher(instance, endpoint, {
        method: "GET",
        authRequired: true,
        scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
    });
};