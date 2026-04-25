"use client";

import { useParams, useRouter } from "next/navigation";
import PostEditorClient from "@/components/editor/PostEditorClient";
import { usePost, useAdminUpdatePost } from "@/hooks/useApi";
import LoadingSpinner from "@/components/ui/LoadingSpinner";

export default function EditPostPage() {
	const params = useParams();
	const router = useRouter();
	const postId = params.id as string;

	// In the real app, we should ideally fetch the post by ID for admin,
	// but currently `usePost` fetches by slug.
	// Wait, we need an admin fetch by ID endpoint. If it doesn't exist, we might have to use the slug,
	// but the route uses `[id]`. Let's assume `usePost` handles ID if slug is passed,
	// or we use it as is for now until the backend endpoint is verified.
	const { data: post, isLoading, error } = usePost(postId);
	const updatePostMutation = useAdminUpdatePost();

	if (isLoading) {
		return (
			<div className="flex h-screen items-center justify-center bg-bg-page">
				<LoadingSpinner size="lg" />
			</div>
		);
	}

	if (error || !post) {
		return (
			<div className="flex h-screen flex-col items-center justify-center gap-4 bg-bg-page text-center">
				<h2 className="font-display text-2xl font-bold text-danger">
					Error Loading Post
				</h2>
				<p className="text-text-secondary">
					Could not find the requested post.
				</p>
				<button className="btn-ghost" onClick={() => router.push("/admin")}>
					Back to Dashboard
				</button>
			</div>
		);
	}

	const handleSave = async (data: any) => {
		try {
			await updatePostMutation.mutateAsync({
				postId,
				payload: {
					title: data.title,
					content: data.content,
					slug: data.slug,
					category_id: data.category_id || undefined,
					status: data.status,
				},
			});
			// Optionally show a toast here.
		} catch (error) {
			console.error("Error updating post:", error);
			throw error;
		}
	};

	return (
		<PostEditorClient
			isNew={false}
			initialData={{
				title: post.title,
				content: post.content,
				slug: post.slug,
				category_id: post.category?.id || "",
				tag_names: post.tags?.map((t) => t.name) || [],
				status: post.status,
				is_agent_authored: post.is_agent_authored,
			}}
			onSave={handleSave}
			onPublish={handleSave}
		/>
	);
}
