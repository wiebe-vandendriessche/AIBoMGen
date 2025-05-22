import {defineRouting} from 'next-intl/routing';
import { createNavigation } from "next-intl/navigation";

export const routing = defineRouting({
  // A list of all locales that are supported
  locales: ['en', 'nl'],
 
  // Used when no locale matches
  defaultLocale: 'en'
});

export type Locale = (typeof routing.locales)[number];
export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);