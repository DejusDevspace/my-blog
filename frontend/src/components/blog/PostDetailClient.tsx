"use client";

import Link from "next/link";
import { format } from "date-fns";
import { Calendar, Clock } from "lucide-react";
import type { Post } from "@/types";
import MarkdownRenderer from "./MarkdownRenderer";
import PostToc from "./PostToc";
import PostComments from "./PostComments";

interface PostDetailClientProps {
	post: Post;
}

export default function PostDetailClient({ post }: PostDetailClientProps) {
	return (
		<div className="mx-auto w-full max-w-300 px-4 pb-24 pt-16 lg:px-8">
			{/* Breadcrumb */}
			<div className="mb-8 font-mono text-xs uppercase text-text-tertiary">
				<Link href="/" className="hover:text-accent transition-colors">
					Home
				</Link>
				<span className="mx-2">/</span>
				<Link href="/blog" className="hover:text-accent transition-colors">
					Blog
				</Link>
				<span className="mx-2">/</span>
				<span>{post.category?.name || "Uncategorized"}</span>
			</div>

			<div className="flex flex-col gap-12 lg:flex-row lg:justify-between">
				{/* Left content area (max-width 720px) */}
				<main className="w-full lg:max-w-180 lg:mx-auto xl:ml-0 xl:mr-auto">
					{/* Post Hero */}
					<header className="mb-10">
						{/* Badge Row */}
						<div className="mb-4 flex gap-2">
							{post.category && (
								<span className="tag uppercase">{post.category.name}</span>
							)}
							{post.is_agent_authored && (
								<span className="badge-agent uppercase">✦ Agent</span>
							)}
						</div>

						{/* Title */}
						<h1 className="mb-6 font-display text-display font-bold leading-tight text-text-primary">
							{post.title}
						</h1>

						{/* Meta Row */}
						<div className="mb-6 flex flex-wrap items-center gap-4 font-mono text-[0.65rem] uppercase text-text-secondary">
							{post.published_at && (
								<div className="flex items-center gap-1.5">
									<Calendar className="h-3.5 w-3.5" />
									<time dateTime={post.published_at}>
										{format(new Date(post.published_at), "MMM d, yyyy")}
									</time>
								</div>
							)}
							<span>·</span>
							<div className="flex items-center gap-1.5">
								<Clock className="h-3.5 w-3.5" />
								<span>{post.reading_time_mins || 5} min read</span>
							</div>
							{post.is_agent_authored && (
								<>
									<span>·</span>
									<span className="text-accent">Written by AI agent</span>
								</>
							)}
						</div>

						{/* Tags */}
						{post.tags && post.tags.length > 0 && (
							<div className="flex flex-wrap gap-2">
								{post.tags.map((tag) => (
									<span key={tag.id} className="tag text-[0.65rem]">
										#{tag.slug}
									</span>
								))}
							</div>
						)}

						<hr className="my-8 border-border-subtle" />
					</header>

					{/* Markdown Body */}
					<article>
						<MarkdownRenderer content={post.content} />
					</article>

					{/* Comments Section */}
					<PostComments postId={post.id} postSlug={post.slug} />
				</main>

				{/* Right TOC Sidebar (sticky, width 260px) */}
				<PostToc content={post.content} />
			</div>
		</div>
	);
}
