import { useMsal } from "@azure/msal-react";

const API_BASE_URL = "http://localhost:8000";

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
        scopes = ["api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation"],
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
        const error = await response.json();
        throw new Error(error.message || "An error occurred while fetching data.");
    }

    return response.json();
};

