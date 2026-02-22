// ============================================================
//  /api/comments — Cloudflare Pages Function
//  GET  ?article_id=xxx  → コメント一覧取得
//  POST { article_id, user_name, body } → コメント投稿
// ============================================================

// CORS headers for cross-origin requests
const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
};

// Handle preflight
export async function onRequestOptions() {
    return new Response(null, { status: 204, headers: corsHeaders });
}

// GET /api/comments?article_id=xxx
export async function onRequestGet(context) {
    const url = new URL(context.request.url);
    const articleId = url.searchParams.get("article_id");

    if (!articleId) {
        return Response.json(
            { error: "article_id is required" },
            { status: 400, headers: corsHeaders }
        );
    }

    try {
        const { results } = await context.env.DB.prepare(
            "SELECT id, article_id, user_name, body, created_at FROM comments WHERE article_id = ? ORDER BY created_at ASC"
        )
            .bind(articleId)
            .all();

        return Response.json(
            { success: true, comments: results },
            { headers: corsHeaders }
        );
    } catch (err) {
        return Response.json(
            { error: "Failed to fetch comments", detail: err.message },
            { status: 500, headers: corsHeaders }
        );
    }
}

// POST /api/comments
export async function onRequestPost(context) {
    let body;
    try {
        body = await context.request.json();
    } catch {
        return Response.json(
            { error: "Invalid JSON body" },
            { status: 400, headers: corsHeaders }
        );
    }

    const { article_id, user_name, body: commentBody } = body;

    // Validation
    if (!article_id || !commentBody) {
        return Response.json(
            { error: "article_id and body are required" },
            { status: 400, headers: corsHeaders }
        );
    }

    // Sanitize: trim and limit lengths
    const safeName = (user_name || "名無しの指揮官さん").trim().slice(0, 50);
    const safeBody = commentBody.trim().slice(0, 1000);

    if (safeBody.length === 0) {
        return Response.json(
            { error: "Comment body cannot be empty" },
            { status: 400, headers: corsHeaders }
        );
    }

    try {
        const result = await context.env.DB.prepare(
            "INSERT INTO comments (article_id, user_name, body, created_at) VALUES (?, ?, ?, datetime('now'))"
        )
            .bind(article_id, safeName, safeBody)
            .run();

        return Response.json(
            { success: true, id: result.meta.last_row_id },
            { status: 201, headers: corsHeaders }
        );
    } catch (err) {
        return Response.json(
            { error: "Failed to save comment", detail: err.message },
            { status: 500, headers: corsHeaders }
        );
    }
}
