/**
 * d3jusdevspace — Global API Types
 *
 * These types mirror the backend Pydantic schemas.
 * Keep them in sync when the backend changes.
 */

/* ============================================================================
  Common / Shared
============================================================================ */

/** Generic paginated response wrapper matching backend `PaginatedResponse[T]`. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

/** Simple message response for confirmations and errors. */
export interface MessageResponse {
  detail: string;
}

/** Standard API error shape returned by FastAPI. */
export interface ApiError {
  detail: string;
  status: number;
}

/* ============================================================================
  Category
============================================================================ */

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  created_at: string;
}

export interface CategoryCreate {
  name: string;
  description?: string | null;
}

export interface CategoryUpdate {
  name?: string | null;
  slug?: string | null;
  description?: string | null;
}

/* ============================================================================
  Tag
============================================================================ */

export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface TagCreate {
  name: string;
}

/* ============================================================================
  Post
============================================================================ */

export type PostStatus = "draft" | "published" | "archived" | "agent_draft";

export interface PostListItem {
  id: string;
  title: string;
  slug: string;
  excerpt: string | null;
  category: Category;
  tags: Tag[];
  status: PostStatus;
  is_agent_authored: boolean;
  reading_time_mins: number | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Post extends PostListItem {
  content: string;
}

export interface PostCreate {
  title: string;
  content: string;
  category_id: string;
  tag_ids?: string[];
  status?: "draft" | "published";
}

export interface PostUpdate {
  title?: string | null;
  slug?: string | null;
  content?: string | null;
  category_id?: string | null;
  tag_ids?: string[] | null;
  status?: PostStatus | null;
}

/* ============================================================================
  Comment
============================================================================ */

export interface Comment {
  id: string;
  post_id: string;
  display_name: string | null;
  body: string;
  created_at: string;
}

export interface CommentCreate {
  post_id: string;
  display_name?: string | null;
  body: string;
  honeypot?: string;
}
