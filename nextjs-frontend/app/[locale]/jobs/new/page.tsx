"use client";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { toast } from "sonner";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";

import { Button } from "@/components/ui/button";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { Label } from "@/components/ui/label";
import { SubmitJob } from "@/services/developer/SubmitJob";
import { useIsAuthenticated, useMsal } from "@azure/msal-react";
import { steps } from "motion/react";

const jobFormSchema = z.object({
    model: z
        .instanceof(File)
        .refine((file) => file.name.endsWith(".keras"), {
            message: "Model file must be a .keras file.",
        }),
    dataset: z
        .instanceof(File)
        .refine(
            (file) =>
                file.name.endsWith(".csv") || file.name.endsWith(".zip"),
            {
                message: "Dataset must be a .csv or .zip file.",
            }
        ),
    dataset_definition: z
        .instanceof(File)
        .refine((file) => file.name.endsWith(".yaml"), {
            message: "Dataset definition must be a .yaml file.",
        }),
    framework: z.literal("TensorFlow 2.16.1"),
    model_name: z.string().optional(),
    model_version: z.string().optional(),
    model_description: z.string().optional(),
    author: z.string().optional(),
    model_type: z.string().optional(),
    base_model: z.string().optional(),
    base_model_source: z.string().optional(),
    intended_use: z.string().optional(),
    out_of_scope: z.string().optional(),
    misuse_or_malicious: z.string().optional(),
    license_name: z.string().optional(),
    epochs: z.number().min(1),
    validation_split: z.number().min(0).max(1),
    initial_epoch: z.number().min(0),
    batch_size: z.number().min(1),
    steps_per_epoch: z.number().min(0),
    validation_steps: z.number().min(0),
    validation_freq: z.number().min(1),
});

type JobFormValues = z.infer<typeof jobFormSchema>;

function capitalize(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

export default function NewJobPage() {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [openItems, setOpenItems] = useState<string[]>([]);

    const { instance } = useMsal();
    const router = useRouter();

    const form = useForm<JobFormValues>({
        resolver: zodResolver(jobFormSchema),
        defaultValues: {
            model: undefined,
            dataset: undefined,
            dataset_definition: undefined,
            framework: "TensorFlow 2.16.1",
            model_name: "",
            model_version: "",
            model_description: "",
            author: "",
            model_type: "",
            base_model: "",
            base_model_source: "",
            intended_use: "",
            out_of_scope: "",
            misuse_or_malicious: "",
            license_name: "",
            epochs: 50, // Matches schema default
            validation_split: 0.2, // Matches schema default
            initial_epoch: 0, // Matches schema default
            batch_size: 32, // Matches schema default
            steps_per_epoch: 0, // Matches schema default
            validation_steps: 0, // Matches schema default
            validation_freq: 1, // Matches schema default
        },
    });

    const onSubmit = async (values: JobFormValues) => {
        setIsSubmitting(true);
        const formData = new FormData();

        Object.entries(values).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                if (value instanceof File) {
                    formData.append(key, value);
                } else {
                    formData.append(key, String(value));
                }
            }
        });

        // Debugging: Log FormData contents
        for (const [key, value] of formData.entries()) {
            console.log(key, value);
        }

        try {
            const result = await SubmitJob(instance, formData);
            console.log("Job submitted successfully:", result);

            // Show success toast
            toast.success("Job created successfully!", {
                description:
                    `Job ID:       ${result.job_id}\n` +
                    `Status:       ${result.status}\n` +
                    `Directory:    ${result.unique_dir}`
                ,
                duration: 15000, // Toast will appear for 15 seconds
            });

            // Redirect to the running job page
            router.push(`/jobs/my/${result.job_id}/running`);

        } catch (error) {
            console.error("Error submitting job:", error);

            // Show error toast
            toast.error("Failed to create the job. Please try again.");

        } finally {
            setIsSubmitting(false);
        }
    };

    const handleValidationErrors = () => {
        // Open all accordion items if there are validation errors
        setOpenItems(["required-parameters", "training-parameters", "user-defined-parameters"]);
    };

    return (
        <div className="max-w-3xl mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Submit a New Job</h1>
            <Form {...form}>
                <form
                    onSubmit={form.handleSubmit(onSubmit, handleValidationErrors)}
                    className="space-y-4"
                >
                    <Accordion
                        type="multiple"
                        className="space-y-3"
                        value={openItems}
                        onValueChange={(values) => setOpenItems(values)}
                    >
                        {/* Required Parameters */}
                        <AccordionItem value="required-parameters">
                            <AccordionTrigger>Required Parameters</AccordionTrigger>
                            <AccordionContent>
                                <FormField
                                    name="model"
                                    control={form.control}
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Model File</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="file"
                                                    accept=".keras"
                                                    onChange={(e) => field.onChange(e.target.files?.[0])}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    name="dataset"
                                    control={form.control}
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Dataset File</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="file"
                                                    accept=".csv,.zip"
                                                    onChange={(e) => field.onChange(e.target.files?.[0])}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    name="dataset_definition"
                                    control={form.control}
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Dataset Definition File</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="file"
                                                    accept=".yaml"
                                                    onChange={(e) => field.onChange(e.target.files?.[0])}
                                                />
                                            </FormControl>
                                            <FormMessage />
                                        </FormItem>
                                    )}
                                />
                                <FormField
                                    name="framework"
                                    control={form.control}
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Framework</FormLabel>
                                            <FormControl>
                                                <Input value={field.value} readOnly />
                                            </FormControl>
                                            <FormDescription>
                                                Currently, only TensorFlow 2.16.1 is supported.
                                            </FormDescription>
                                        </FormItem>
                                    )}
                                />
                            </AccordionContent>
                        </AccordionItem>

                        {/* Training Parameters */}
                        <AccordionItem value="training-parameters">
                            <AccordionTrigger>Training Parameters</AccordionTrigger>
                            <AccordionContent>
                                {([
                                    "epochs",
                                    "validation_split",
                                    "initial_epoch",
                                    "batch_size",
                                    "steps_per_epoch",
                                    "validation_steps",
                                    "validation_freq",
                                ] as const).map((fieldName) => {
                                    const fieldConstraints: Record<string, { min?: number; max?: number; step?: string }> = {
                                        validation_split: { min: 0, max: 1, step: "any" },
                                        epochs: { min: 1, step: "1" },
                                        initial_epoch: { min: 0, step: "1" },
                                        batch_size: { min: 1, step: "1" },
                                        validation_freq: { min: 1, step: "1" },
                                    };

                                    const constraints = fieldConstraints[fieldName] || {};

                                    return (
                                        <FormField
                                            key={fieldName}
                                            name={fieldName}
                                            control={form.control}
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>{capitalize(fieldName.replace(/_/g, " "))}</FormLabel>
                                                    <FormControl>
                                                        <Input
                                                            type="number"
                                                            placeholder={`Enter ${fieldName}`}
                                                            value={field.value || ""}
                                                            min={constraints.min}
                                                            max={constraints.max}
                                                            step={constraints.step}
                                                            onChange={(e) =>
                                                                field.onChange(
                                                                    e.target.value === "" ? undefined : Number(e.target.value)
                                                                )
                                                            }
                                                        />
                                                    </FormControl>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />
                                    );
                                })}
                            </AccordionContent>
                        </AccordionItem>

                        {/* User Defined Parameters */}
                        <AccordionItem value="user-defined-parameters">
                            <AccordionTrigger>User Defined Parameters</AccordionTrigger>
                            <AccordionContent>
                                <p className="text-sm text-gray-600 mb-4">
                                    Optional user input params will be included in the AIBoM but are not trusted truth because the author of a model can write what they want. However, we guarantee that the author specified these as recorded in the AIBoM.
                                </p>
                                {([
                                    "model_name",
                                    "model_version",
                                    "model_description",
                                    "author",
                                    "model_type",
                                    "base_model",
                                    "base_model_source",
                                    "intended_use",
                                    "out_of_scope",
                                    "misuse_or_malicious",
                                    "license_name",
                                ] as const).map((fieldName) => (
                                    <FormField
                                        key={fieldName}
                                        name={fieldName}
                                        control={form.control}
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>
                                                    {capitalize(fieldName.replace(/_/g, " "))} (Optional)
                                                </FormLabel>
                                                <FormControl>
                                                    {["model_description", "intended_use", "out_of_scope", "misuse_or_malicious"].includes(fieldName) ? (
                                                        <Textarea placeholder={`Enter ${fieldName}`} {...field} />
                                                    ) : (
                                                        <Input placeholder={`Enter ${fieldName}`} {...field} />
                                                    )}
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                ))}
                            </AccordionContent>
                        </AccordionItem>
                    </Accordion>

                    {/* Submit Button */}
                    <Button type="submit" disabled={isSubmitting}>
                        {isSubmitting ? "Submitting..." : "Submit Job"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}
