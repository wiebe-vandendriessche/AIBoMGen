import { Configuration, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.CLIENT_ID || "", // Use CLIENT_ID from .env
    authority: "https://login.microsoftonline.com/common",
    redirectUri: process.env.REDIRECT_URI || "", // Use REDIRECT_URI from .env
    postLogoutRedirectUri: process.env.POST_LOGOUT_REDIRECT_URI || "", // Use POST_LOGOUT_REDIRECT_URI from .env
    navigateToLoginRequestUrl: false,
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
    process.env.BACKEND_SCOPE || "", // Use BACKEND_SCOPE from .env
    "User.Read",
  ],
};