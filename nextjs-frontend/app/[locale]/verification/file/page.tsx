"use client";

import { useState } from "react";
import { VerifyFileHash } from "@/services/verifier/VerifyFileHash";
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
import { useRouter } from "next/navigation";
import { AlertCircle } from "lucide-react";
import { useTranslations } from "next-intl";

const verifySchema = z.object({
    link_file: z
        .instanceof(File)
        .refine((file) => file.name.endsWith(".link"), {
            message: "Link file must be a .link file.",
        }),
    uploaded_file: z
        .instanceof(File)
        .refine((file) => !!file.name, {
            message: "Please select a file to verify.",
        }),
});

type VerifyFormValues = z.infer<typeof verifySchema>;

export default function VerifyFileHashPage() {
    const [loading, setLoading] = useState(false);
    const { instance } = useMsal();
    const router = useRouter();
    const t = useTranslations("Verification");

    const form = useForm<VerifyFormValues>({
        resolver: zodResolver(verifySchema),
        defaultValues: {
            link_file: undefined,
            uploaded_file: undefined,
        },
    });

    const onSubmit = async (values: VerifyFormValues) => {
        setLoading(true);
        const formData = new FormData();
        formData.append("link_file", values.link_file);
        formData.append("uploaded_file", values.uploaded_file);

        try {
            const result = await VerifyFileHash(formData, instance);
            if (result.status === "success") {
                toast.success("Hash matches!", {
                    description: (
                        <div>
                            <div>{result.message}</div>
                            <ul className="mt-2 ml-4 list-disc text-sm">
                                <li>
                                    <span className="font-semibold">File:</span> {result.details.file_name}
                                </li>
                                <li>
                                    <span className="font-semibold">Hash:</span> {JSON.stringify(result.details.hash)}
                                </li>
                            </ul>
                        </div>
                    ),
                    duration: 10000,
                });
            } else {
                toast.error("Hash mismatch!", {
                    description: (
                        <div>
                            <div>{result.message}</div>
                            <ul className="mt-2 ml-4 list-disc text-sm">
                                <li>
                                    <span className="font-semibold">File:</span> {result.details.file_name}
                                </li>
                                <li>
                                    <span className="font-semibold">Computed hash:</span> {JSON.stringify(result.details.computed_hash)}
                                </li>
                                <li>
                                    <span className="font-semibold">Recorded hash:</span> {JSON.stringify(result.details.recorded_hash)}
                                </li>
                            </ul>
                        </div>
                    ),
                    duration: 15000,
                });
            }
        } catch (err: any) {
            let errorMsg = "Verification failed: " + (err?.message || "Unknown error");
            if (err?.response) {
                try {
                    const data = await err.response.json?.();
                    if (data?.detail) {
                        errorMsg = data.detail;
                    }
                } catch { }
            }
            if (err?.detail) {
                errorMsg = err.detail;
            }
            toast.error(errorMsg);
        }
        setLoading(false);
    };

    return (
        <div className="max-w-3xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">{t("verifyFileHashTitle")}</h1>
            <Alert variant="destructive" className="mb-6 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 mt-1" />
                <div>
                    <AlertTitle>{t("important")}</AlertTitle>
                    <AlertDescription>
                        {t("linkFileFirst")}
                        <br />
                        <Button
                            variant="outline"
                            size="sm"
                            className="mt-2"
                            onClick={() => router.push("/verification/link")}
                        >
                            {t("gotoLinkVerification")}
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
                                        accept=".link"
                                        onChange={(e) => field.onChange(e.target.files?.[0])}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        name="uploaded_file"
                        control={form.control}
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>{t("fileToVerifyLabel")}</FormLabel>
                                <FormControl>
                                    <Input
                                        type="file"
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