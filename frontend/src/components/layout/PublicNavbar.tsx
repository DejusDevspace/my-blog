"use client";

import Link from "next/link";
import { Search, Moon, Monitor } from "lucide-react";
import { useEffect, useState } from "react";

export default function PublicNavbar() {
	const [theme, setTheme] = useState<"light" | "dark">("dark");

	// Initial theme setup (simplified for now, assumes dark is default as per spec)
	useEffect(() => {
		const stored = localStorage.getItem("theme");
		if (stored === "light") {
			// eslint-disable-next-line react-hooks/set-state-in-effect
			setTheme("light");
			document.documentElement.setAttribute("data-theme", "light");
		} else {
			// eslint-disable-next-line react-hooks/set-state-in-effect
			setTheme("dark");
			document.documentElement.setAttribute("data-theme", "dark");
		}
	}, []);

	const toggleTheme = () => {
		const newTheme = theme === "dark" ? "light" : "dark";
		setTheme(newTheme);
		localStorage.setItem("theme", newTheme);
		document.documentElement.setAttribute("data-theme", newTheme);
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
							placeholder="Search neural architectures..."
							className="input w-full bg-bg-page pl-10"
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
						{theme === "dark" ? (
							<Monitor className="h-5 w-5" />
						) : (
							<Moon className="h-5 w-5" />
						)}
					</button>

					<a
						href="https://github.com/d3jus"
						target="_blank"
						rel="noopener noreferrer"
						className="hidden md:inline-flex rounded border border-border-default px-3 py-1.5 font-mono text-sm text-accent hover:border-accent hover:bg-accent-muted transition-colors"
					>
						GitHub
					</a>
				</div>
			</div>
		</nav>
	);
}
