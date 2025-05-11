import { Configuration, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: "eae0c268-a92d-46cc-b66f-bc9aca2281c4", // Replace with your Azure AD App's Client ID
    authority: "https://login.microsoftonline.com/common", // Use the common endpoint for multi-tenant
    redirectUri: "http://localhost:3000",
    postLogoutRedirectUri: "http://localhost:3000", // Redirect URI after logout
    navigateToLoginRequestUrl: false, // Set to true if you want to redirect to the login page after login
  },
  cache: {
    cacheLocation: "sessionStorage", // Use sessionStorage to store tokens
    storeAuthStateInCookie: false,
  },
  system: {
    loggerOptions: {
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) {
          return;
        }
        switch (level) {
          case LogLevel.Error:
            console.error(message);
            return;
          case LogLevel.Info:
            console.info(message);
            return;
          case LogLevel.Verbose:
            console.debug(message);
            return;
          case LogLevel.Warning:
            console.warn(message);
            return;
        }
      },
      logLevel: LogLevel.Verbose,
      piiLoggingEnabled: false,
    },
  },
};

export const loginRequest = {
  scopes: [
    "api://a65becdd-c8b9-4a90-9c8a-9d9c526aa130/user_impersonation", // Replace with the Backend API App's scope
    "User.Read", // Required for fetching profile photo
  ],
};