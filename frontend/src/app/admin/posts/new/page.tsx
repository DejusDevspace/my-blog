"use client";

import { useRouter } from "next/navigation";
import PostEditorClient from "@/components/editor/PostEditorClient";
import { useAdminCreatePost } from "@/hooks/useApi";

export default function NewPostPage() {
	const router = useRouter();
	const createPostMutation = useAdminCreatePost();

	const handleSave = async (data: any) => {
		try {
			// Convert tags from array of names to what the backend might expect,
			// or if backend expects names, just pass it. For now, assuming tag_names isn't in PostCreate
			// but we just pass the bare minimum to create it.
			// Actually, the API type `PostCreate` expects `tag_ids`.
			// Since we just have tag names from the UI, we might need a separate call or backend handles it.
			// For this implementation, we will omit tags or pass an empty array if backend requires IDs.

			const newPost = await createPostMutation.mutateAsync({
				title: data.title || "Untitled",
				content: data.content,
				category_id: data.category_id || undefined,
				status: data.status,
			} as any);

			// On success, redirect to the edit page to avoid creating duplicates on subsequent saves
			router.push(`/admin/posts/${newPost.id}/edit`);
		} catch (error) {
			console.error("Error creating post:", error);
			throw error;
		}
	};

	return (
		<PostEditorClient
			isNew={true}
			initialData={{}}
			onSave={handleSave}
			onPublish={handleSave}
		/>
	);
}
