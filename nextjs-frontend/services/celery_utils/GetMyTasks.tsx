import { fetcher } from "../api";

export const GetMyTasks = async (instance: any) => {
    const endpoint = `/celery_utils/tasks/my`;
    return await fetcher(instance, endpoint, {
        method: "GET",
        authRequired: true,
        scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
    });
};