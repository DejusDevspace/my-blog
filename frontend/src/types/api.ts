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
  Series
============================================================================ */

/** Minimal series info embedded in post responses. */
export interface PostSeriesInfo {
  id: string;
  title: string;
  slug: string;
  series_order: number | null;
}

/** Series list item with post count (used in feeds and admin list). */
export interface SeriesListItem {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  status: string;
  post_count: number;
  created_at: string;
  updated_at: string;
}

/** Minimal post data within a series response. */
export interface SeriesPostItem {
  id: string;
  title: string;
  slug: string;
  series_order: number | null;
  status: string;
  published_at: string | null;
}

/** Full series with ordered posts. */
export interface SeriesResponse {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  status: string;
  posts: SeriesPostItem[];
  created_at: string;
  updated_at: string;
}

export interface SeriesCreate {
  title: string;
  description?: string | null;
  status?: "draft" | "published";
}

export interface SeriesUpdate {
  title?: string | null;
  slug?: string | null;
  description?: string | null;
  status?: string | null;
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
  series: PostSeriesInfo | null;
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
  tags?: string[];
  series_id?: string | null;
  series_order?: number | null;
  status?: "draft" | "published";
}

export interface PostUpdate {
  title?: string | null;
  slug?: string | null;
  content?: string | null;
  category_id?: string | null;
  tags?: string[] | null;
  series_id?: string | null;
  series_order?: number | null;
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
