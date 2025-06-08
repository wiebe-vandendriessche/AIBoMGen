import { useMsal } from "@azure/msal-react";

const API_BASE_URL = process.env.API_BASE_URL || ""; // Use API_BASE_URL from .env

const getAccessToken = async (instance: any, scopes: string[]) => {
    const activeAccount = instance.getActiveAccount();
    if (!activeAccount) {
        throw new Error("No active account found. Please log in.");
    }

    const tokenResponse = await instance.acquireTokenSilent({
        scopes,
        account: activeAccount,
    });

    return tokenResponse.accessToken;
};

export const fetcher = async (
    instance: any, // Pass instance from useMsal
    endpoint: string,
    {
        method = "GET",
        body = null,
        queryParams = {},
        authRequired = false,
        scopes = [process.env.BACKEND_SCOPE || ""], // Use BACKEND_SCOPE from .env
    }: {
        method?: string;
        body?: any;
        queryParams?: Record<string, string>;
        authRequired?: boolean;
        scopes?: string[];
    }
) => {
    const queryString = new URLSearchParams(queryParams).toString();
    const url = `${API_BASE_URL}${endpoint}${queryString ? `?${queryString}` : ""}`;

    // Initialize headers
    const headers: Record<string, string> = {};

    // Add Authorization header if required
    if (authRequired) {
        const token = await getAccessToken(instance, scopes);
        headers["Authorization"] = `Bearer ${token}`;
    }

    // Only set Content-Type if the body is not FormData
    if (body && !(body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(body); // Convert body to JSON if it's not FormData
    }

    const response = await fetch(url, {
        method,
        headers,
        body: body || null, // Pass body directly (FormData or JSON)
    });

    if (!response.ok) {
        let errorDetail = "An error occurred while fetching data.";
        try {
            const error = await response.json();
            if (error?.detail) {
                errorDetail = error.detail;
            } else if (error?.message) {
                errorDetail = error.message;
            }
            // Attach the detail to the error object for further inspection
            const err = new Error(errorDetail);
            (err as any).detail = errorDetail;
            throw err;
        } catch {
            // If response is not JSON, throw generic error
            const err = new Error(errorDetail);
            (err as any).detail = errorDetail;
            throw err;
        }
    }

    return response.json();
};

