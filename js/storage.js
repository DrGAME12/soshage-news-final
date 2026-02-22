// ============================================================
//  SOSHAGESHIN — LocalStorage Manager
//  Handles history, bookmarks, resume, read status, reactions
// ============================================================

const SoshageshinStorage = (() => {
    const KEYS = {
        HISTORY: 'soshageshin_history',
        RESUME: 'soshageshin_resume',
        BOOKMARKS: 'soshageshin_bookmarks',
        REACTIONS: 'soshageshin_reactions',
        THEME: 'soshageshin_theme'
    };

    function _get(key, fallback) {
        try { return JSON.parse(localStorage.getItem(key)) || fallback; }
        catch { return fallback; }
    }
    function _set(key, val) {
        localStorage.setItem(key, JSON.stringify(val));
    }

    // ── HISTORY (最近読んだ号) ──
    // Array of { id, game, title, date, path, timestamp }
    function getHistory() { return _get(KEYS.HISTORY, []); }

    function addHistory(entry) {
        const hist = getHistory().filter(h => h.id !== entry.id);
        hist.unshift({ ...entry, timestamp: Date.now() });
        _set(KEYS.HISTORY, hist.slice(0, 30)); // keep last 30
    }

    // ── RESUME (続きから読む) ──
    // { [issueId]: scrollRatio }
    function getResume(issueId) {
        const data = _get(KEYS.RESUME, {});
        return data[issueId] || 0;
    }

    function setResume(issueId, scrollRatio) {
        const data = _get(KEYS.RESUME, {});
        data[issueId] = scrollRatio;
        _set(KEYS.RESUME, data);
    }

    function clearResume(issueId) {
        const data = _get(KEYS.RESUME, {});
        delete data[issueId];
        _set(KEYS.RESUME, data);
    }

    // ── BOOKMARKS (お気に入り) ──
    // Array of game slugs
    function getBookmarks() { return _get(KEYS.BOOKMARKS, []); }

    function isBookmarked(slug) { return getBookmarks().includes(slug); }

    function toggleBookmark(slug) {
        const bm = getBookmarks();
        const idx = bm.indexOf(slug);
        if (idx >= 0) bm.splice(idx, 1); else bm.push(slug);
        _set(KEYS.BOOKMARKS, bm);
        return idx < 0; // true = now bookmarked
    }

    // ── READ STATUS (既読判定 → NEWバッジ) ──
    function isRead(issueId) {
        return getHistory().some(h => h.id === issueId);
    }

    // ── REACTIONS ──
    // { [issueId]: { '🔥': count, '👍': count, '💀': count } }
    function getReactions(issueId) {
        const data = _get(KEYS.REACTIONS, {});
        return data[issueId] || {};
    }

    function addReaction(issueId, emoji) {
        const data = _get(KEYS.REACTIONS, {});
        if (!data[issueId]) data[issueId] = {};
        data[issueId][emoji] = (data[issueId][emoji] || 0) + 1;
        _set(KEYS.REACTIONS, data);
        return data[issueId][emoji];
    }

    function hasReacted(issueId, emoji) {
        const reacted = _get('soshageshin_reacted', {});
        return reacted[`${issueId}_${emoji}`] === true;
    }

    function markReacted(issueId, emoji) {
        const reacted = _get('soshageshin_reacted', {});
        reacted[`${issueId}_${emoji}`] = true;
        _set('soshageshin_reacted', reacted);
    }

    // ── THEME ──
    function getTheme() { return _get(KEYS.THEME, 'dark'); }
    function setTheme(theme) { _set(KEYS.THEME, theme); }

    // ── COMMENTS ──
    // { [issueId]: [ { name, text, timestamp }, ... ] }
    function getComments(issueId) {
        const data = _get('soshageshin_comments', {});
        return data[issueId] || [];
    }

    function addComment(issueId, name, text) {
        const data = _get('soshageshin_comments', {});
        if (!data[issueId]) data[issueId] = [];
        data[issueId].push({ name: name || '名無しの指揮官さん', text, timestamp: Date.now() });
        _set('soshageshin_comments', data);
        return data[issueId];
    }

    // ── COMMENT LIKES ──
    // { "issueId:idx": likeCount }
    function getCommentLikes(issueId, idx) {
        const data = _get('soshageshin_comment_likes', {});
        return data[issueId + ':' + idx] || 0;
    }

    function likeComment(issueId, idx) {
        const key = issueId + ':' + idx;
        const data = _get('soshageshin_comment_likes', {});
        data[key] = (data[key] || 0) + 1;
        _set('soshageshin_comment_likes', data);
        // Track that this user liked it
        const liked = _get('soshageshin_comment_liked', {});
        liked[key] = true;
        _set('soshageshin_comment_liked', liked);
    }

    function hasLikedComment(issueId, idx) {
        const liked = _get('soshageshin_comment_liked', {});
        return !!liked[issueId + ':' + idx];
    }

    return {
        getHistory, addHistory,
        getResume, setResume, clearResume,
        getBookmarks, isBookmarked, toggleBookmark,
        isRead,
        getReactions, addReaction, hasReacted, markReacted,
        getTheme, setTheme,
        getComments, addComment,
        getCommentLikes, likeComment, hasLikedComment
    };
})();
