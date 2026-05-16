import { SITE } from "@/lib/constants";

/**
 * robots.txt — allows all crawlers on public pages,
 * blocks the admin panel and API routes.
 */
export default function robots() {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin/", "/api/"],
      },
    ],
    sitemap: `${SITE.url}/sitemap.xml`,
  };
}
