"use client";

import { Sparkles } from "lucide-react";

interface HeroSectionProps {
	totalPosts: number;
}

export default function HeroSection({ totalPosts }: HeroSectionProps) {
	return (
		<div className="w-full flex justify-end bg-bg-page border-t-2 border-accent/80 pt-10 pb-8 px-4 lg:px-8">
			<div className="mx-auto max-w-7xl flex flex-col items-start gap-4">
				{/* Headline */}
				<h1 className="flex items-center flex-wrap gap-2 text-h2 md:text-display font-display font-bold text-text-primary">
					Hi, I&apos;m{" "}
					<span
						className="inline-block rounded-full bg-accent px-4 py-1 text-bg-page"
						style={{ boxShadow: "var(--shadow-neon-accent)" }}
					>
						d3ju
					</span>
				</h1>

				{/* Sub-headline */}
				<p className="max-w-2xl font-body text-body-lg text-text-secondary">
					AI/ML Engineer documenting the frontier of neural networks, computer
					vision, and the agentic age.
				</p>

				{/* Post count */}
				<div className="mt-4 flex items-center gap-2 rounded border border-accent/30 bg-accent-muted px-3 py-1.5 font-mono text-xs uppercase tracking-wider text-accent shadow-sm">
					<Sparkles className="h-3.5 w-3.5" />
					<span>{totalPosts} POSTS PUBLISHED</span>
				</div>
			</div>
		</div>
	);
}
