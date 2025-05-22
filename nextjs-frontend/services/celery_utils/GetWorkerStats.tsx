import { fetcher } from "../api";

export const GetWorkersStats = async (instance?: any) => {
    const endpoint = `/celery_utils/workers/stats`;
    return await fetcher(instance, endpoint, {
        method: "GET",
        authRequired: false,
        scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
    });
};