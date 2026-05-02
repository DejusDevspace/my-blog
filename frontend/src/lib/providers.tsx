/**
 * d3jusdevspace — Client Providers
 *
 * Wraps the app in:
 *  1. React Query (data fetching / caching)
 *  2. Persisted cache (localStorage — instant loads on return visits)
 *  3. next-themes (theme toggling)
 */

"use client";

import { useState, type ReactNode } from "react";
import { QueryClient } from "@tanstack/react-query";
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { createAsyncStoragePersister } from "@tanstack/query-async-storage-persister";
import { ThemeProvider } from "next-themes";
import { ToastProvider } from "@/context/ToastContext";

interface ProvidersProps {
	children: ReactNode;
}

// localStorage persister — survives page reloads and browser restarts.
// Only persists queries with gcTime > 0 (which is all of them by default).
const persister =
	typeof window !== "undefined"
		? createAsyncStoragePersister({
				storage: window.localStorage,
				key: "d3jusdevspace-cache",
			})
		: undefined;

export default function Providers({ children }: ProvidersProps) {
	// Create a stable QueryClient per React tree (avoids sharing across requests in SSR)
	const [queryClient] = useState(
		() =>
			new QueryClient({
				defaultOptions: {
					queries: {
						// Baseline: 2 min stale, 30 min GC.
						// Individual hooks override staleTime for data that changes less.
						staleTime: 2 * 60 * 1000, // 2 minutes
						gcTime: 30 * 60 * 1000, // 30 minutes
						refetchOnWindowFocus: false,
						retry: 1,
					},
				},
			}),
	);

	return (
		<PersistQueryClientProvider
			client={queryClient}
			persistOptions={{
				persister: persister!,
				// Max age for persisted cache: 24 hours.
				// After that, cache is discarded and fresh data is fetched.
				maxAge: 24 * 60 * 60 * 1000,
				// Only persist public data — skip admin queries.
				dehydrateOptions: {
					shouldDehydrateQuery: (query) => {
						const key = query.queryKey[0] as string;
						return key !== "admin" && key !== "health";
					},
				},
			}}
		>
			<ThemeProvider
				attribute="data-theme"
				defaultTheme="dark"
				enableSystem={false}
				disableTransitionOnChange
			>
				<ToastProvider>{children}</ToastProvider>
			</ThemeProvider>
		</PersistQueryClientProvider>
	);
}
