"""
SEO routes: /robots.txt and /sitemap.xml

Usage in your main.py:

    from app.seo import seo_router
    app.include_router(seo_router)

Both routes use APP_BASE_URL from your .env, so you don't need to
hardcode the domain anywhere — change it once in .env and both
routes update automatically.
"""

import os
from datetime import date

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

seo_router = APIRouter()

# Falls back to a placeholder if APP_BASE_URL isn't set, so it still
# returns something instead of crashing.
BASE_URL = os.getenv("APP_BASE_URL", "https://yourdomain.com").rstrip("/")


@seo_router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
def robots_txt():
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /docs
Disallow: /redoc
Disallow: /openapi.json

Sitemap: {BASE_URL}/sitemap.xml
"""
    return PlainTextResponse(content)


@seo_router.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    # Add real public-facing pages here as your frontend grows.
    # Pure API JSON endpoints should NOT be listed — sitemaps are for
    # crawlable content pages only.
    pages = [
        {"loc": "/", "priority": "1.0"},
    ]

    today = date.today().isoformat()
    urls = "\n".join(
        f"""  <url>
    <loc>{BASE_URL}{p['loc']}</loc>
    <lastmod>{today}</lastmod>
    <priority>{p['priority']}</priority>
  </url>"""
        for p in pages
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""

    return Response(content=xml, media_type="application/xml")
