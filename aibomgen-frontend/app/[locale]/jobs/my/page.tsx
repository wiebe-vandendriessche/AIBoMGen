"use client";

import { useEffect, useState } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { GetMyTasks } from "@/services/celery_utils/GetMyTasks";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { Clipboard, ExternalLink, ArrowUpDown } from "lucide-react";
import Link from "next/link";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { toast } from "sonner";
import {
  ColumnDef,
  SortingState,
  ColumnFiltersState,
  getCoreRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  useReactTable,
} from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import React from "react";
import { useJobContext } from "@/components/context/JobContext";
import { useTranslations } from "next-intl";

const MyJobsPage = () => {
  const { instance, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const { jobs, setJobs } = useJobContext(); // Access the context to set jobs
  const [loading, setLoading] = useState(true);
  const t = useTranslations("Jobs");

  useEffect(() => {
    const fetchJobs = async () => {
      if (inProgress !== InteractionStatus.None || !isAuthenticated) {
        return; // Wait for MSAL to finish initializing and ensure the user is authenticated
      }

      try {
        const data = await GetMyTasks(instance);
        setJobs(data);
      } catch (error) {
        console.error("Error fetching jobs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs(); // Fetch jobs immediately on mount

    // Polling mechanism: Fetch jobs every 30 seconds
    const interval = setInterval(() => {
      fetchJobs();
    }, 30000); // 30 seconds

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [instance, inProgress, isAuthenticated, setJobs]);

  const columns: ColumnDef<any>[] = [
    {
      accessorKey: "id",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {t("id")}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(row.getValue("id"));
                    toast.success(t("copiedJobId"));
                  }}
                >
                  <Clipboard className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {t("copyJobId")}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <span>{row.getValue("id")}</span>
        </div>
      ),
    },
    {
      accessorKey: "state",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {t("state")}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => row.getValue("state"),
    },
    {
      accessorKey: "result.training_status",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {t("trainingStatus")}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => row.original.result?.training_status || t("na"),
    },
    {
      accessorKey: "result.unique_dir",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {t("uniqueDirectory")}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => row.original.result?.unique_dir || t("na"),
    },
    {
      accessorKey: "date_done",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          {t("dateDone")}
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const dateDone = row.getValue("date_done");
        if (!dateDone) return t("na");

        return `${dateDone} UTC`;
      },
    },
    {
      id: "actions",
      header: t("actions"),
      cell: ({ row }) => (
        <Link href={`/jobs/my/${row.getValue("id")}`}>
          <Button variant="ghost" size="sm">
            <ExternalLink className="h-4 w-4" />
            {t("open")}
          </Button>
        </Link>
      ),
    },
  ];

  const [sorting, setSorting] = React.useState<SortingState>([
    { id: "date_done", desc: true }, // Sort by date_done in descending order
  ]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  );

  const table = useReactTable({
    data: jobs,
    columns,
    state: { sorting, columnFilters },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  // Show a warning if the user is not authenticated
  if (!isAuthenticated) {
    return (
      <div className="p-6 flex justify-center">
        <Alert className="max-w-xl w-full border-red-400" variant="destructive">
          <AlertCircle className="h-6 w-6" />
          <div>
            <AlertTitle>{t("accessDenied")}</AlertTitle>
            <AlertDescription>
              {t("notLoggedIn")}
            </AlertDescription>
          </div>
        </Alert>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">{t("myJobsTitle")}</h1>
        <div className="flex items-center py-4">
          <Skeleton className="h-10 w-64" />
        </div>
        <ScrollArea className="w-full">
          <div className="min-w-[1000px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t("id")}</TableHead>
                  <TableHead>{t("state")}</TableHead>
                  <TableHead>{t("trainingStatus")}</TableHead>
                  <TableHead>{t("uniqueDirectory")}</TableHead>
                  <TableHead>{t("dateDone")}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Array.from({ length: 10 }).map((_, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Skeleton className="h-4 w-16" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-32" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-20" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-32" />
                    </TableCell>
                    <TableCell>
                      <Skeleton className="h-4 w-32" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </ScrollArea>
        <div className="flex items-center justify-end space-x-2 py-4">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-8 w-24" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">{t("myJobsTitle")}</h1>
      <div className="flex items-center py-4">
        <Input
          placeholder={t("filterJobsById")}
          className="max-w-sm"
          value={(table.getColumn("id")?.getFilterValue() as string) ?? ""}
          onChange={(e) =>
            table.getColumn("id")?.setFilterValue(e.target.value)
          }
        />
      </div>
      <ScrollArea className="w-full">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="text-center">
                  {t("noResults")}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>

      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          {t("previous")}
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          {t("next")}
        </Button>
      </div>
    </div>
  );
};

export default MyJobsPage;