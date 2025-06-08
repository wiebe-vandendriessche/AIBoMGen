"use client";

import { useState } from "react";
import { VerifyMinioArtifacts } from "@/services/verifier/VerifyMinioArtifacts";
import { Button } from "@/components/ui/button";
import {
    Form,
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { useMsal } from "@azure/msal-react";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

const verifySchema = z.object({
    link_file: z
        .instanceof(File)
        .refine((file) => file.name.endsWith(".link"), {
            message: "Link file must be a .link file.",
        }),
});

type VerifyFormValues = z.infer<typeof verifySchema>;

export default function VerifyMinioStoragePage() {
    const [loading, setLoading] = useState(false);
    const { instance } = useMsal();
    const t = useTranslations("Verification");

    const form = useForm<VerifyFormValues>({
        resolver: zodResolver(verifySchema),
        defaultValues: {
            link_file: undefined,
        },
    });

    const onSubmit = async (values: VerifyFormValues) => {
        setLoading(true);
        const formData = new FormData();
        formData.append("link_file", values.link_file);

        try {
            const result = await VerifyMinioArtifacts(formData, instance);
            if (result.status === "success") {
                toast.success("Verification successful!", {
                    description: "All materials and products matched. MinIO object storage is verified.",
                    duration: 10000,
                });
            } else {
                toast.error("Verification failed!", {
                    description: (
                        <div>
                            <div>
                                <strong>Mismatched Materials:</strong>
                                {result.mismatched_materials.length === 0
                                    ? " None"
                                    : (
                                        <ul className="ml-4 list-disc">
                                            {result.mismatched_materials.map((mat: any, idx: number) => (
                                                <li key={idx}>
                                                    <div>
                                                        <span className="font-mono">{mat.path}</span>
                                                        <br />
                                                        <span className="text-xs">
                                                            <strong>Computed:</strong> {mat.computed_hash?.sha256}
                                                            <br />
                                                            <strong>Recorded:</strong> {mat.recorded_hash?.sha256}
                                                        </span>
                                                    </div>
                                                </li>
                                            ))}
                                        </ul>
                                    )
                                }
                            </div>
                            <div className="mt-2">
                                <strong>Mismatched Products:</strong>
                                {result.mismatched_products.length === 0
                                    ? " None"
                                    : (
                                        <ul className="ml-4 list-disc">
                                            {result.mismatched_products.map((prod: any, idx: number) => (
                                                <li key={idx}>
                                                    <div>
                                                        <span className="font-mono">{prod.path}</span>
                                                        <br />
                                                        <span className="text-xs">
                                                            <strong>Computed:</strong> {prod.computed_hash?.sha256}
                                                            <br />
                                                            <strong>Recorded:</strong> {prod.recorded_hash?.sha256}
                                                        </span>
                                                    </div>
                                                </li>
                                            ))}
                                        </ul>
                                    )
                                }
                            </div>
                        </div>
                    ),
                    duration: 15000,
                });
            }
        } catch (err: any) {
            toast.error("Verification failed: " + (err?.message || "Unknown error"));
        }
        setLoading(false);
    };

    return (
        <div className="max-w-3xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">{t("verifyMinioTitle")}</h1>
            <Alert variant="destructive" className="mb-6 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 mt-1" />
                <div>
                    <AlertTitle>{t("important")}</AlertTitle>
                    <AlertDescription>
                        {t("linkFileFirst")}
                        <br />
                        <Button
                            asChild
                            variant="outline"
                            size="sm"
                            className="mt-2"
                        >
                            <Link href="/verification/link">
                                {t("gotoLinkVerification")}
                            </Link>
                        </Button>
                    </AlertDescription>
                </div>
            </Alert>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        name="link_file"
                        control={form.control}
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>{t("linkFileLabel")}</FormLabel>
                                <FormControl>
                                    <Input
                                        type="file"
                                        accept=".link,.json"
                                        onChange={(e) => field.onChange(e.target.files?.[0])}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? t("verifying") : t("verify")}
                    </Button>
                </form>
            </Form>
        </div>
    );
}