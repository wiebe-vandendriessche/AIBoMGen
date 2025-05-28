"use client";

import { useState } from "react";
import { VerifyInTotoLink } from "@/services/verifier/VerifyInTotoLink";
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
import { useTranslations } from "next-intl";

const verifySchema = z.object({
    link_file: z
        .instanceof(File)
        .refine((file) => file.name.endsWith(".link"), {
            message: "Link file must be a .link file.",
        }),
});

type VerifyFormValues = z.infer<typeof verifySchema>;

export default function VerifyInTotoLinkPage() {
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
            const result = await VerifyInTotoLink(formData, instance);
            toast.success("Verification successful!", {
                description: (
                    <div>
                        <div>{result.message || "Link file verification successful."}</div>
                        {result.details && (
                            <ul className="mt-2 ml-4 list-disc text-sm">
                                {Object.entries(result.details).map(([key, value]) => (
                                    <li key={key}>
                                        <span className="font-semibold">{key.replace(/_/g, " ")}:</span> {String(value)}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                ),
                duration: 10000,
            });
        } catch (err: any) {
            let errorMsg = "Verification failed: " + (err?.message || "Unknown error");
            if (err?.response) {
                try {
                    const data = await err.response.json?.();
                    if (data?.detail) {
                        errorMsg = data.detail;
                    }
                } catch {
                    // ignore JSON parse errors
                }
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
            <h1 className="text-2xl font-bold mb-4">{t("verifyLinkTitle")}</h1>
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
                    <Button type="submit" disabled={loading}>
                        {loading ? t("verifying") : t("verify")}
                    </Button>
                </form>
            </Form>
        </div>
    );
}