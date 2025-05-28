import { fetcher } from "../api";

export const VerifyBomAndLink = async (formData: FormData, instance: any) => {
    const endpoint = `/verifier/verify_bom_and_link`;
    return await fetcher(instance, endpoint, {
        method: "POST",
        body: formData,
        authRequired: false,
        scopes: ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
    });
};