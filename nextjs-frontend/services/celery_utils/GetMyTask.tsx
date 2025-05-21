import { fetcher } from "../api";

export const GetMyTask = async (instance: any, jobId: string) => {
    const endpoint = `/celery_utils/tasks/my/${jobId}`;
    return await fetcher(instance, endpoint, {
        method: "GET",
        authRequired: true,
        scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
    });
};