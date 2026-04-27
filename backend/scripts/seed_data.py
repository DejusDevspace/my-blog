#!/usr/bin/env python3
"""Seed categories and tags for the blog.

Usage:
    python scripts/seed_data.py

Idempotent — skips any category/tag that already exists (matched by slug).
Requires the owner to be seeded first (run seed_owner.py beforehand).
"""

import asyncio

from slugify import slugify
from sqlalchemy import select

from app.db.base import async_session_factory
from app.models.category import Category
from app.models.owner import Owner
from app.models.post import Tag

# ---------------------------------------------------------------------------
# Starting Categories and Tags
# ---------------------------------------------------------------------------

CATEGORIES: list[dict[str, str]] = [
    {
        "name": "Projects",
        "description": "Deep dives into projects I've built or am currently building — architecture, trade-offs, and lessons learned.",
    },
    {
        "name": "AI & Machine Learning",
        "description": "Explorations in AI/ML — models, pipelines, tools, and research notes.",
    },
    {
        "name": "Backend/Systems Engineering",
        "description": "APIs, databases, system design, and server-side patterns, embedded systems and robotics.",
    },
    {
        "name": "Frontend/Mobile Engineering",
        "description": "UI development, design systems, frameworks, and mobile development.",
    },
    {
        "name": "DevOps & Infra",
        "description": "CI/CD, containers, deployments, and cloud infrastructure.",
    },
    {
        "name": "Thoughts",
        "description": "Opinions, reflections, and essays on tech and engineering culture.",
    },
]

TAGS: list[str] = [
    # Languages & runtimes
    "Python",
    "TypeScript",
    "JavaScript",
    "C++",
    "SQL",
    # Frameworks — backend
    "FastAPI",
    "SQLAlchemy",
    "Django",
    "Flask",
    "Node.js",
    # Frameworks — frontend
    "Next.js",
    "React",
    "Tailwind CSS",
    # AI / ML
    "LangChain",
    "LangGraph",
    "LLM",
    "NLP",
    "RAG",
    "Fine-Tuning",
    "Computer Vision",
    "PyTorch",
    "Scikit-Learn",
    "Hugging Face",
    # Robotics and Embedded Systems
    "Arduino",
    "Raspberry Pi",
    "ESP32",
    "Robotics",
    "Embedded Systems",
    "IoT",
    "ROS",
    "ROS2",
    # Data
    "PostgreSQL",
    "Redis",
    "pgvector",
    "Pandas",
    # OS & System
    "Linux",
    # DevOps & Cloud
    "Docker",
    "GitHub Actions",
    "Vercel",
    "Netlify",
    "Azure",
    "GCP",
    "Cloudinary",
    "Railway",
    "AWS",
    "Supabase",
    "Neon",
    # Concepts
    "System Design",
    "API Design",
    "Authentication",
    "Testing",
    "Performance",
    "Open Source",
    # AI Tools
    "ollama",
    "llama.cpp",
    "Claude",
    "Claude Code",
    "ChatGPT",
    "Gemini",
    "Antigravity",
    "Codex",
    #
    "Personal Development",
    "Learning",
    "Documentation",
    "Tutorials",
    "Career",
    "Books",
    "Productivity",
]


async def seed() -> None:
    async with async_session_factory() as session:
        # --- Resolve the owner ---
        result = await session.execute(select(Owner).limit(1))
        owner = result.scalar_one_or_none()
        if owner is None:
            print("ERROR: No owner found. Run seed_owner.py first.")
            return

        owner_id = owner.id
        print(f"Using owner: {owner.email} (id={owner_id})\n")

        # --- Seed categories ---
        print("Categories:")
        for cat_data in CATEGORIES:
            slug = slugify(cat_data["name"])
            existing = await session.execute(
                select(Category).where(
                    Category.owner_id == owner_id,
                    Category.slug == slug,
                )
            )
            if existing.scalar_one_or_none():
                print(f"  ✓ {cat_data['name']} (already exists)")
                continue

            category = Category(
                owner_id=owner_id,
                name=cat_data["name"],
                slug=slug,
                description=cat_data.get("description"),
            )
            session.add(category)
            print(f"  + {cat_data['name']}")

        await session.flush()

        # --- Seed tags ---
        print("\nTags:")
        for tag_name in TAGS:
            slug = slugify(tag_name)
            existing = await session.execute(
                select(Tag).where(
                    Tag.owner_id == owner_id,
                    Tag.slug == slug,
                )
            )
            if existing.scalar_one_or_none():
                print(f"  ✓ {tag_name} (already exists)")
                continue

            tag = Tag(owner_id=owner_id, name=tag_name, slug=slug)
            session.add(tag)
            print(f"  + {tag_name}")

        await session.commit()
        print("\nDone.")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
