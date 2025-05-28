import { fetcher } from "../api";

export const SubmitJob = async (instance: any, formData: FormData) => {
  const endpoint = `/developer/submit_job_by_model_and_data`;

  return await fetcher(instance, endpoint, {
    method: "POST",
    body: formData, // Pass FormData directly
    authRequired: true,
    scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
  });
};