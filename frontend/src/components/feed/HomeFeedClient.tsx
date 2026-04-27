"use client";

import { useState, useEffect } from "react";
import { usePosts } from "@/hooks/useApi";
import { useSearchParams, useRouter } from "next/navigation";
import HeroSection from "./HeroSection";
import FilterSidebar from "./FilterSidebar";
import PostCard from "./PostCard";
import type { PostListItem } from "@/types";
import { FileText, FilterX, Loader2 } from "lucide-react";

export default function HomeFeedClient() {
	const searchParams = useSearchParams();
	const router = useRouter();

	const activeCategory = searchParams.get("category");
	const activeTag = searchParams.get("tag");

	const [page, setPage] = useState(1);
	const [allPosts, setAllPosts] = useState<PostListItem[]>([]);

	const { data, isLoading, isFetching, error } = usePosts({
		page,
		limit: 10,
		category: activeCategory || undefined,
		tag: activeTag || undefined,
	});

	// Reset posts and page when filters change
	useEffect(() => {
		// eslint-disable-next-line react-hooks/set-state-in-effect
		setPage(1);
		// eslint-disable-next-line react-hooks/set-state-in-effect
		setAllPosts([]);
	}, [activeCategory, activeTag]);

	// Accumulate posts when data changes
	useEffect(() => {
		if (data?.items) {
			if (page === 1) {
				// eslint-disable-next-line react-hooks/set-state-in-effect
				setAllPosts(data.items);
			} else {
				// eslint-disable-next-line react-hooks/set-state-in-effect
				setAllPosts((prev) => {
					// Prevent duplicates
					const existingIds = new Set(prev.map((p) => p.id));
					const newPosts = data.items.filter((p) => !existingIds.has(p.id));
					return [...prev, ...newPosts];
				});
			}
		}
	}, [data, page]);

	const updateFilter = (type: "category" | "tag", value: string | null) => {
		const params = new URLSearchParams(searchParams.toString());
		if (value) {
			params.set(type, value);
		} else {
			params.delete(type);
		}
		router.push(`/?${params.toString()}`);
	};

	const hasMore = data ? data.page < data.pages : false;

	return (
		<>
			<HeroSection totalPosts={data?.total || 0} />

			<div className="mx-auto flex w-full max-w-7xl flex-col gap-12 px-4 py-12 lg:flex-row lg:px-8">
				<FilterSidebar
					activeCategory={activeCategory}
					activeTag={activeTag}
					onCategoryChange={(cat) => updateFilter("category", cat)}
					onTagChange={(tag) => updateFilter("tag", tag)}
				/>

				<div className="flex-1">
					{(activeCategory || activeTag) && (
						<div className="mb-6 flex items-center justify-between rounded bg-bg-elevated px-4 py-3 border border-border-default">
							<span className="font-mono text-xs uppercase text-text-secondary">
								Showing filters:{" "}
								{activeCategory && (
									<span className="text-accent">{activeCategory}</span>
								)}
								{activeCategory && activeTag && " + "}
								{activeTag && <span className="text-accent">{activeTag}</span>}
							</span>
							<button
								onClick={() => router.push("/")}
								className="flex items-center gap-1 font-mono text-[0.65rem] uppercase text-text-tertiary hover:text-danger transition-colors"
							>
								<FilterX className="h-3 w-3" />
								Clear
							</button>
						</div>
					)}

					{isLoading && page === 1 ? (
						<div className="flex flex-col gap-5">
							{[1, 2, 3, 4].map((i) => (
								<div
									key={i}
									className="h-48 w-full rounded-xl border border-border-subtle bg-bg-surface p-6 skeleton"
								/>
							))}
						</div>
					) : error ? (
						<div className="flex flex-col items-center justify-center py-20 text-center">
							<p className="font-display text-h3 text-danger">
								Couldn&apos;t load posts
							</p>
							<p className="text-text-secondary">
								Something went wrong. Try refreshing.
							</p>
						</div>
					) : allPosts.length === 0 ? (
						<div className="flex flex-col items-center justify-center py-20 text-center">
							<FileText className="mb-4 h-12 w-12 text-text-tertiary" />
							<p className="mb-2 font-display text-h3 text-text-primary">
								Nothing here yet
							</p>
							<p className="text-text-secondary">
								{activeCategory || activeTag
									? "No posts match this filter."
									: "Check back soon — content is on the way."}
							</p>
						</div>
					) : (
						<div className="flex flex-col gap-5">
							{allPosts.map((post) => (
								<PostCard key={post.id} post={post} />
							))}

							{hasMore && (
								<div className="mt-8 flex justify-center">
									<button
										onClick={() => setPage((p) => p + 1)}
										disabled={isFetching}
										className="btn-primary uppercase text-xs tracking-wider"
									>
										{isFetching ? (
											<>
												<Loader2 className="h-4 w-4 animate-spin" /> Loading...
											</>
										) : (
											"Load More"
										)}
									</button>
								</div>
							)}
						</div>
					)}
				</div>
			</div>
		</>
	);
}
