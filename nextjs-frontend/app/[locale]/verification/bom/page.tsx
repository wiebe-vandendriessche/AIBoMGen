"use client";

import { useState } from "react";
import { VerifyBomAndLink } from "@/services/verifier/VerifyBomAndLink";
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

const verifySchema = z.object({
    bom_file: z
        .instanceof(File)
        .refine((file) => file.name.endsWith(".json") || file.name.endsWith(".xml"), {
            message: "BOM file must be a .json or .xml file.",
        }),
});

type VerifyFormValues = z.infer<typeof verifySchema>;

export default function VerifyAIBOMPage() {
    const [loading, setLoading] = useState(false);
    const { instance } = useMsal();

    const form = useForm<VerifyFormValues>({
        resolver: zodResolver(verifySchema),
        defaultValues: {
            bom_file: undefined,
        },
    });

    const onSubmit = async (values: VerifyFormValues) => {
        setLoading(true);
        const formData = new FormData();
        formData.append("bom_file", values.bom_file);

        try {
            const result = await VerifyBomAndLink(formData, instance);
            toast.success("Verification successful!", {
                description: (
                    <div>
                        <div>{result.message || "BOM and .link file verification successful."}</div>
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
            // Try to extract backend error message from err.response or err.detail
            if (err?.response) {
                try {
                    // Try to parse the response as JSON
                    const data = await err.response.json?.();
                    if (data?.detail) {
                        errorMsg = data.detail;
                    }
                } catch {
                    // ignore JSON parse errors
                }
            }
            // If err.detail is present directly on the error object
            if (err?.detail) {
                errorMsg = err.detail;
            }
            toast.error(errorMsg);
        }
        setLoading(false);
    };

    return (
        <div className="max-w-3xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Verify AIBOM</h1>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                        name="bom_file"
                        control={form.control}
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>BOM File</FormLabel>
                                <FormControl>
                                    <Input
                                        type="file"
                                        accept=".json,.xml"
                                        onChange={(e) => field.onChange(e.target.files?.[0])}
                                    />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button type="submit" disabled={loading}>
                        {loading ? "Verifying..." : "Verify"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}