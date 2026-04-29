/**
 * d3jusdevspace — Client Providers
 *
 * Wraps the app in:
 *  1. React Query (data fetching / caching)
 *  2. next-themes (theme toggling)
 */

"use client";

import { useState, type ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { ToastProvider } from "@/context/ToastContext";

interface ProvidersProps {
	children: ReactNode;
}

export default function Providers({ children }: ProvidersProps) {
	// Create a stable QueryClient per React tree (avoids sharing across requests in SSR)
	const [queryClient] = useState(
		() =>
			new QueryClient({
				defaultOptions: {
					queries: {
						staleTime: 60 * 1000, // 1 minute
						refetchOnWindowFocus: false,
						retry: 1,
					},
				},
			}),
	);

	return (
		<QueryClientProvider client={queryClient}>
			<ThemeProvider
				attribute="data-theme"
				defaultTheme="dark"
				enableSystem={false}
				disableTransitionOnChange
			>
				<ToastProvider>{children}</ToastProvider>
			</ThemeProvider>
		</QueryClientProvider>
	);
}
