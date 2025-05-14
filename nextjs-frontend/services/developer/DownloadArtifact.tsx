import { fetcher } from "../api";

export const DownloadArtifact = async (
    instance: any,
    jobId: string,
    artifactName: string
) => {
    const endpoint = `/developer/job_artifacts/${jobId}/${artifactName}`;
    return await fetcher(instance, endpoint, {
        method: "GET",
        authRequired: true,
        scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
    });
};