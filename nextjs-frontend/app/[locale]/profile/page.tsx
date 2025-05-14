"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { useMsal } from "@azure/msal-react";
import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { useTranslations } from "next-intl";

const Profile = () => {
  const { instance, accounts } = useMsal();
  const [profile, setProfile] = useState<any>(null);
  const [profilePicture, setProfilePicture] = useState<string | null>(null);
  const t = useTranslations("Profile");

  useEffect(() => {
    const fetchProfile = async () => {
      if (accounts.length > 0) {
        try {
          const tokenResponse = await instance.acquireTokenSilent({
            scopes: ["User.Read"], // Microsoft Graph scope
            account: accounts[0],
          });

          const accessToken = tokenResponse.accessToken;

          // Fetch profile details
          const profileResponse = await fetch("https://graph.microsoft.com/v1.0/me", {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          });

          if (profileResponse.ok) {
            const profileData = await profileResponse.json();
            setProfile(profileData);
          } else {
            console.error("Error fetching profile:", await profileResponse.json());
          }

          // Fetch profile picture
          const pictureResponse = await fetch("https://graph.microsoft.com/v1.0/me/photo/$value", {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          });

          if (pictureResponse.ok) {
            const blob = await pictureResponse.blob();
            const pictureUrl = URL.createObjectURL(blob);
            setProfilePicture(pictureUrl);
          } else {
            console.warn("No profile picture found. Falling back to default.");
            setProfilePicture(null);
          }
        } catch (error) {
          console.error("Error fetching profile or picture:", error);
        }
      }
    };

    fetchProfile();
  }, [accounts, instance]);

  // If no account is logged in, show the Guest Profile
  if (accounts.length === 0) {
    return (
      <div className="p-4 flex justify-center overflow-x-clip">
        <Card className="w-full max-w-xl">
          <CardHeader className="flex flex-col items-center">
            {/* Guest Profile Picture */}
            <Avatar className="w-24 h-24 mb-4">
              <AvatarImage
                src={"https://ui-avatars.com/api/?name=g"}
                alt={t("guestProfilePicture")}
              />
              <AvatarFallback>G</AvatarFallback>
            </Avatar>
            <CardTitle>{t("guestUser")}</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className="mt-4 border-red-400" variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>{t("warning")}</AlertTitle>
              <AlertDescription>{t("guestWarning")}</AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  // If profile is still loading, show Skeleton placeholders
  if (!profile) {
    return (
      <div className="p-4 flex justify-center">
        <Card className="w-full max-w-xl">
          <CardHeader className="flex flex-col items-center">
            {/* Skeleton for Profile Picture */}
            <Skeleton className="w-24 h-24 rounded-full mb-4" />
            {/* Skeleton for Name */}
            <Skeleton className="w-32 h-6 mb-2" />
            {/* Skeleton for Description */}
            <Skeleton className="w-48 h-4" />
          </CardHeader>
          <CardContent>
            {/* Skeleton for Profile Details */}
            <Skeleton className="w-full h-4 mb-2" />
            <Skeleton className="w-3/4 h-4 mb-2" />
            <Skeleton className="w-2/3 h-4" />
          </CardContent>
        </Card>
      </div>
    );
  }

  // Logged-in user profile
    return (
    <div className="p-4 flex justify-center">
      <Card className="w-full max-w-xl">
        <CardHeader className="flex flex-col items-center">
          <Avatar className="w-24 h-24 mb-4">
            {profilePicture ? (
              <AvatarImage src={profilePicture} alt={t("profilePicture")} />
            ) : (
              <AvatarFallback>{profile.displayName.charAt(0)}</AvatarFallback>
            )}
          </Avatar>
          <CardTitle>{profile.displayName}</CardTitle>
          <CardDescription>{profile.mail || profile.userPrincipalName}</CardDescription>
        </CardHeader>
        <CardContent>
          <p><strong>{t("email")}:</strong> {profile.mail || profile.userPrincipalName}</p>
          {profile.jobTitle && <p><strong>{t("jobTitle")}:</strong> {profile.jobTitle}</p>}
          {profile.department && <p><strong>{t("department")}:</strong> {profile.department}</p>}
          {profile.officeLocation && <p><strong>{t("officeLocation")}:</strong> {profile.officeLocation}</p>}
          {profile.mobilePhone && <p><strong>{t("mobilePhone")}:</strong> {profile.mobilePhone}</p>}
          {profile.businessPhones?.[0] && (
            <p><strong>{t("businessPhone")}:</strong> {profile.businessPhones[0]}</p>
          )}
          {profile.preferredLanguage && (
            <p><strong>{t("preferredLanguage")}:</strong> {profile.preferredLanguage}</p>
          )}
          {profile.country && <p><strong>{t("country")}:</strong> {profile.country}</p>}
          {profile.city && <p><strong>{t("city")}:</strong> {profile.city}</p>}
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;