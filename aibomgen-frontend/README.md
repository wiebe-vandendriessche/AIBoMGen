# AIBoMGen Frontend

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

---

## Getting Started

### Prerequisites

- **Backend API:** The backend must be running and accessible at the correct URL.
- **Authentication:** The backend **must** have authentication enabled (`AUTH_ENABLED=true`). The frontend will not work without authentication.
- **Azure App Registration:**  
  - You need to register an application in Azure AD for the frontend.
  - This app registration must have delegated permissions to access the backend API (the backend's app registration).
  - Configure the required API permissions in Azure and grant admin consent.

### Setup

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   # or
   bun install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   # or
   bun dev
   ```

3. **Build and run in production:**
   ```bash
   npm run build
   npm run start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Configuration

- **MSAL Configuration:**  
  Edit `components/configurations/msalConfig.tsx` and set:
  - `clientId` to your frontend Azure App Registration's client ID.
  - `authority` to your Azure tenant or use `common` for multi-tenant.
  - `redirectUri` and `postLogoutRedirectUri` as needed.
  - The `scopes` in `loginRequest` must match the exposed API scope of your backend app registration (e.g., `api://<backend-app-id>/user_impersonation`).

- **API Service:**  
  Edit `services/api.tsx` and set:
  - `API_BASE_URL` to your backend's URL (default: `http://localhost:8000`).
  - The `scopes` parameter in API calls must match your backend API's scope.

---

## Authentication

- The frontend uses MSAL (Microsoft Authentication Library) for Azure OAuth authentication.
- Users must sign in with an account that has access to the backend API via the configured Azure App Registrations and permissions.

---

## Fonts

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font).

---

## Deployment

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme).

Check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---

## Learn More

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [Next.js GitHub repository](https://github.com/vercel/next.js)