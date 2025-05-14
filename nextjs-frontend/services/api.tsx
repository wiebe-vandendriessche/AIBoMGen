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

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
    };

    if (authRequired) {
        const token = await getAccessToken(instance, scopes);
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "An error occurred while fetching data.");
    }

    return response.json();
};

