"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Moon, Sun, Loader2, Layers } from "lucide-react";
import { useTheme } from "next-themes";

export default function PublicNavbar() {
	const { theme, setTheme } = useTheme();
	const [mounted, setMounted] = useState(false);

	// Avoid hydration mismatch — theme is undefined on the server.
	useEffect(() => setMounted(true), []);

	const toggleTheme = () => {
		setTheme(theme === "dark" ? "light" : "dark");
	};

	return (
		<nav className="sticky top-0 z-50 h-16 w-full border-b border-border-subtle bg-bg-surface">
			<div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 lg:px-8">
				{/* Brand */}
				<Link
					href="/"
					className="font-mono text-lg font-bold tracking-wider text-accent uppercase"
					style={{ textShadow: "var(--shadow-neon-accent)" }}
				>
					d3jusdevspace
				</Link>

				{/* Center: Search (Desktop) */}
				<div className="hidden md:flex flex-1 items-center justify-center px-8">
					<div className="relative w-full max-w-100">
						<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-tertiary" />
						<input
							type="text"
							placeholder="Search posts..."
							className="input w-full bg-bg-page pl-10!"
						/>
					</div>
				</div>

				{/* Right: Actions */}
				<div className="flex items-center gap-4">
					<button
						onClick={toggleTheme}
						className="rounded-md p-2 text-text-secondary hover:bg-bg-elevated hover:text-text-primary transition-colors"
						aria-label="Toggle theme"
					>
						{mounted ? (
							theme === "dark" ? (
								<Sun className="h-5 w-5" />
							) : (
								<Moon className="h-5 w-5" />
							)
						) : (
							<div className="h-5 w-5" />
						)}
					</button>

					<Link
						href="/series"
						className="hidden md:inline-flex items-center gap-1.5 rounded border border-border-default px-3 py-1.5 font-mono text-sm text-text-secondary hover:border-accent hover:text-accent transition-colors"
					>
						<Layers size={12} />
						Series
					</Link>

					<a
						href="https://github.com/DejusDevspace/my-blog"
						target="_blank"
						rel="noopener noreferrer"
						className="hidden md:inline-flex rounded border border-border-default px-3 py-1.5 font-mono text-sm text-accent hover:border-accent hover:bg-accent-muted transition-colors"
					>
						GitHub
					</a>
				</div>
			</div>

			{/* Mobile Search Panel */}
			{isMobileSearchOpen && (
				<div className="md:hidden border-t border-border-subtle bg-bg-surface px-4 py-3 shadow-md">
					{renderSearchBar(mobileSearchRef, true)}
					<div className="mt-3 flex items-center gap-3 border-t border-border-subtle pt-3">
						<Link
							href="/series"
							className="flex items-center gap-1.5 text-sm font-mono text-text-secondary hover:text-accent transition-colors"
							onClick={() => setIsMobileSearchOpen(false)}
						>
							<Layers size={12} />
							Series
						</Link>
					</div>
				</div>
			)}
		</nav>
	);
}
