/**
 * d3jusdevspace — React Query Hooks
 *
 * Thin wrappers around the service layer that provide loading, error, and
 * caching semantics via @tanstack/react-query.
 */

"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryOptions,
  type UseMutationOptions,
} from "@tanstack/react-query";
import type {
  ApiError,
  Category,
  Comment,
  CommentCreate,
  MessageResponse,
  PaginatedResponse,
  Post,
  PostCreate,
  PostListItem,
  PostUpdate,
} from "@/types";
import * as api from "@/services/api";
import type { ListPostsParams, AdminListPostsParams } from "@/services/api";

/* ============================================================================
  Query Key Factory — keeps cache keys consistent
============================================================================ */

export const queryKeys = {
  posts: {
    all: ["posts"] as const,
    list: (params?: ListPostsParams) => ["posts", "list", params] as const,
    detail: (slug: string) => ["posts", "detail", slug] as const,
    comments: (slug: string) => ["posts", "comments", slug] as const,
  },
  admin: {
    posts: {
      all: ["admin", "posts"] as const,
      list: (params?: AdminListPostsParams) =>
        ["admin", "posts", "list", params] as const,
      detail: (id: string) => ["admin", "posts", "detail", id] as const,
    },
    categories: {
      all: ["admin", "categories"] as const,
    },
  },
  health: ["health"] as const,
} as const;

/* ============================================================================
  Public — Posts
============================================================================ */

/** Fetch paginated published posts. */
export function usePosts(
  params: ListPostsParams = {},
  options?: Partial<
    UseQueryOptions<PaginatedResponse<PostListItem>, ApiError>
  >,
) {
  return useQuery<PaginatedResponse<PostListItem>, ApiError>({
    queryKey: queryKeys.posts.list(params),
    queryFn: () => api.listPublishedPosts(params),
    ...options,
  });
}

/** Fetch a single published post by slug. */
export function usePost(
  slug: string,
  options?: Partial<UseQueryOptions<Post, ApiError>>,
) {
  return useQuery<Post, ApiError>({
    queryKey: queryKeys.posts.detail(slug),
    queryFn: () => api.getPostBySlug(slug),
    enabled: !!slug,
    ...options,
  });
}

/* ============================================================================
  Public — Comments
============================================================================ */

/** Fetch approved comments for a post. */
export function usePostComments(
  slug: string,
  options?: Partial<UseQueryOptions<Comment[], ApiError>>,
) {
  return useQuery<Comment[], ApiError>({
    queryKey: queryKeys.posts.comments(slug),
    queryFn: () => api.getPostComments(slug),
    enabled: !!slug,
    ...options,
  });
}

/** Submit a comment — invalidates the comment list on success. */
export function useSubmitComment(
  options?: UseMutationOptions<Comment, ApiError, CommentCreate>,
) {
  const queryClient = useQueryClient();

  return useMutation<Comment, ApiError, CommentCreate>({
    mutationFn: api.submitComment,
    onSuccess: (_data, variables) => {
      // We don't know the slug from variables alone — invalidate all comments.
      queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
    ...options,
  });
}

/* ============================================================================
  Admin — Posts
============================================================================ */

/** (Admin) Fetch all posts. */
export function useAdminPosts(
  params: AdminListPostsParams = {},
  options?: Partial<
    UseQueryOptions<PaginatedResponse<PostListItem>, ApiError>
  >,
) {
  return useQuery<PaginatedResponse<PostListItem>, ApiError>({
    queryKey: queryKeys.admin.posts.list(params),
    queryFn: () => api.adminListPosts(params),
    ...options,
  });
}

/** (Admin) Fetch a single post by ID. */
export function useAdminPost(
  postId: string,
  options?: Partial<UseQueryOptions<Post, ApiError>>,
) {
  return useQuery<Post, ApiError>({
    queryKey: queryKeys.admin.posts.detail(postId),
    queryFn: () => api.adminGetPostById(postId),
    enabled: !!postId,
    ...options,
  });
}

/** (Admin) Create a post. */
export function useAdminCreatePost(
  options?: UseMutationOptions<Post, ApiError, PostCreate>,
) {
  const queryClient = useQueryClient();
  return useMutation<Post, ApiError, PostCreate>({
    mutationFn: api.adminCreatePost,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.admin.posts.all,
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
    ...options,
  });
}

/** (Admin) Update a post. */
export function useAdminUpdatePost(
  options?: UseMutationOptions<
    Post,
    ApiError,
    { postId: string; payload: PostUpdate }
  >,
) {
  const queryClient = useQueryClient();
  return useMutation<
    Post,
    ApiError,
    { postId: string; payload: PostUpdate }
  >({
    mutationFn: ({ postId, payload }) =>
      api.adminUpdatePost(postId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.admin.posts.all,
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
    ...options,
  });
}

/** (Admin) Delete a post. */
export function useAdminDeletePost(
  options?: UseMutationOptions<MessageResponse, ApiError, string>,
) {
  const queryClient = useQueryClient();
  return useMutation<MessageResponse, ApiError, string>({
    mutationFn: api.adminDeletePost,
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.admin.posts.all,
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
    ...options,
  });
}

/* ============================================================================
  Admin — Categories
============================================================================ */

/** (Admin) Fetch all categories. */
export function useAdminCategories(
  options?: Partial<UseQueryOptions<Category[], ApiError>>,
) {
  return useQuery<Category[], ApiError>({
    queryKey: queryKeys.admin.categories.all,
    queryFn: api.adminListCategories,
    ...options,
  });
}

/* ============================================================================
  Health
============================================================================ */

/** Check backend health. */
export function useHealthCheck(
  options?: Partial<UseQueryOptions<{ status: string }, ApiError>>,
) {
  return useQuery<{ status: string }, ApiError>({
    queryKey: queryKeys.health,
    queryFn: api.healthCheck,
    retry: false,
    ...options,
  });
}
