"use client";

import { MsalProvider } from "@azure/msal-react";
import { PublicClientApplication } from "@azure/msal-browser";
import { msalConfig } from "../configurations/msalConfig";

const msalInstance = new PublicClientApplication(msalConfig);

export default function MsalProviderWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MsalProvider instance={msalInstance}>{children}</MsalProvider>;
}