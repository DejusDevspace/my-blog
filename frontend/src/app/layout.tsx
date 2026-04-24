import type { Metadata } from "next";
import "./globals.css";
import Providers from "@/lib/providers";

export const metadata: Metadata = {
	title: {
		default: "d3jusdevspace",
		template: "%s — d3jusdevspace",
	},
	description:
		"Personal AI knowledge hub, engineering blog, and agentic AI observability platform.",
	metadataBase: new URL(
		process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
	),
	openGraph: {
		type: "website",
		siteName: "d3jusdevspace",
		locale: "en_US",
	},
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body className="min-h-screen bg-bg-page text-text-primary font-body antialiased">
				<Providers>{children}</Providers>
			</body>
		</html>
	);
}
