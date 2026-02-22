// ============================================================
//  SOSHAGESHIN — Vertical Scroll PDF Viewer v2
//  Features: lazy loading, progress, resume, reactions, sharing
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    initViewer();
    initViewerAppBar();
    initViewerMenu();
    initViewerSearch();
});

function initViewer() {
    const viewerEl = document.getElementById('viewerPages');
    const metaEl = document.getElementById('viewerMeta');
    if (!viewerEl || !metaEl) return;

    const meta = {
        title: metaEl.dataset.title || 'Dispatch',
        pageCount: parseInt(metaEl.dataset.pagecount || '0', 10),
        date: metaEl.dataset.date || '',
        basePath: metaEl.dataset.basepath || './',
        pdfFile: metaEl.dataset.pdffile || 'original.pdf',
        hasImages: metaEl.dataset.hasimages === 'true',
        game: metaEl.dataset.game || '',
        gameSlug: metaEl.dataset.gameslug || '',
        summary: metaEl.dataset.summary || '',
        tags: metaEl.dataset.tags ? metaEl.dataset.tags.split(',') : []
    };

    const issueId = `${meta.gameSlug}_${meta.date}`;

    // Set header
    const titleEl = document.getElementById('viewerTitle');
    if (titleEl) titleEl.textContent = meta.title;

    const dlEl = document.getElementById('viewerDownload');
    if (dlEl) { dlEl.href = meta.basePath + meta.pdfFile; dlEl.download = meta.pdfFile; }

    // Record in history
    SoshageshinStorage.addHistory({
        id: issueId,
        game: meta.game,
        title: meta.title,
        date: meta.date,
        path: window.location.href
    });

    // Render info header (above pages)
    renderInfoHeader(viewerEl, meta, issueId);

    // Render pages
    renderPages(viewerEl, meta);

    // Init features
    initProgressBar(meta.pageCount);
    initResume(issueId);
    renderReactions(issueId);
    renderShareBar(meta.title);
    renderSummary(meta);
    renderComments(issueId);
    renderRelated(meta);
}

// ── INFO HEADER (metadata section above pages) ──
function renderInfoHeader(container, meta, issueId) {
    const reactions = SoshageshinStorage.getReactions(issueId);
    const likeCount = Object.values(reactions).reduce((s, n) => s + n, 0);
    const isBm = SoshageshinStorage.isBookmarked(meta.gameSlug);
    const dateJp = meta.date.replace(/(\d{4})-(\d{2})-(\d{2})/, '$1年$2月$3日');

    // Find game info from registry
    let gameIcon = '';
    let gameColor = 'var(--gold)';
    if (typeof GAMES !== 'undefined') {
        const g = GAMES.find(g => g.slug === meta.gameSlug);
        if (g) { gameIcon = g.icon; gameColor = g.color; }
    }

    const header = document.createElement('div');
    header.className = 'viewer-info';
    header.innerHTML = `
        <div class="viewer-info__topline">
            <span class="viewer-info__date">📅 ${dateJp}</span>
            <span class="viewer-info__badge" style="background: ${gameColor}">戦報</span>
            <span class="viewer-info__likes">❤ ${likeCount}+</span>
        </div>
        <h2 class="viewer-info__title">${meta.title}</h2>
        <div class="viewer-info__actions">
            <span class="viewer-info__pages">${meta.pageCount}ページ</span>
            <button class="viewer-info__bookmark ${isBm ? 'viewer-info__bookmark--active' : ''}"
                onclick="onViewerBookmark('${meta.gameSlug}', this)">
                🔖 ${isBm ? 'ブックマーク済み' : 'マイリストに追加'}
            </button>
        </div>
        <table class="viewer-info__table">
            <tr>
                <th>ゲーム</th>
                <td><a href="../../../../games/${meta.gameSlug}/index.html" class="viewer-info__game-link">${gameIcon} ${meta.game}</a></td>
            </tr>
            ${meta.summary ? `<tr><th>概要</th><td>${meta.summary}</td></tr>` : ''}
            ${meta.tags.length ? `
            <tr>
                <th>タグ</th>
                <td class="viewer-info__tagcell">
                    ${meta.tags.map(t => `<span class="tag-chip">${t}</span>`).join('  ')}
                </td>
            </tr>` : ''}
        </table>
    `;
    container.parentNode.insertBefore(header, container);
}

function onViewerBookmark(slug, btn) {
    const nowBm = SoshageshinStorage.toggleBookmark(slug);
    btn.classList.toggle('viewer-info__bookmark--active', nowBm);
    btn.textContent = nowBm ? '🔖 ブックマーク済み' : '🔖 マイリストに追加';
}

// ── RENDER PAGES ──
function renderPages(container, meta) {
    let html = '';
    for (let i = 1; i <= meta.pageCount; i++) {
        const num = String(i).padStart(2, '0');
        if (meta.hasImages) {
            html += `
        <div class="viewer-page-item" data-page="${i}">
          <img src="${meta.basePath}page-${num}.webp" alt="Page ${i}" loading="${i <= 2 ? 'eager' : 'lazy'}" decoding="async">
          <span class="viewer-page-item__number">${i} / ${meta.pageCount}</span>
        </div>`;
        } else {
            html += `
        <div class="viewer-page-placeholder" data-page="${i}">
          <div class="viewer-page-placeholder__num">${num}</div>
          <div class="viewer-page-placeholder__label">PDF PAGE ${i} / ${meta.pageCount}</div>
        </div>`;
        }
    }
    container.innerHTML = html;
}

// ── PROGRESS BAR + PAGE COUNTER ──
function initProgressBar(pageCount) {
    const bar = document.getElementById('progressBar');
    const ind = document.getElementById('pageIndicator');
    if (!bar || !ind) return;

    const pages = document.querySelectorAll('[data-page]');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                ind.textContent = `${e.target.dataset.page} / ${pageCount}`;
            }
        });
    }, { threshold: 0.5, rootMargin: '-20% 0px -50% 0px' });

    pages.forEach(p => observer.observe(p));

    window.addEventListener('scroll', () => {
        const ratio = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
        bar.style.width = Math.min(ratio * 100, 100) + '%';
    }, { passive: true });
}

// ── RESUME (続きから読む) ──
function initResume(issueId) {
    const savedRatio = SoshageshinStorage.getResume(issueId);

    if (savedRatio > 0.05) {
        // Show resume banner
        const banner = document.createElement('div');
        banner.className = 'resume-banner';
        banner.innerHTML = `
      📖 前回の続きから読む
      <button class="resume-banner__dismiss" onclick="this.parentElement.remove()">✕</button>
    `;
        banner.onclick = (e) => {
            if (e.target.closest('.resume-banner__dismiss')) return;
            const target = (document.documentElement.scrollHeight - window.innerHeight) * savedRatio;
            window.scrollTo({ top: target, behavior: 'smooth' });
            banner.remove();
        };
        document.body.appendChild(banner);

        // Auto-dismiss after 5s
        setTimeout(() => banner.remove(), 8000);
    }

    // Save scroll position periodically
    let saveTimer;
    window.addEventListener('scroll', () => {
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => {
            const ratio = window.scrollY / Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
            if (ratio > 0.02) {
                SoshageshinStorage.setResume(issueId, ratio);
            }
            // If user reached the end, clear resume
            if (ratio > 0.95) {
                SoshageshinStorage.clearResume(issueId);
            }
        }, 500);
    }, { passive: true });
}

// ── LIKE BUTTON ──
function renderReactions(issueId) {
    const footer = document.querySelector('.viewer-footer');
    if (!footer) return;

    const existing = SoshageshinStorage.getReactions(issueId);
    const likeCount = existing['\u2764\ufe0f'] || 0;
    const hasLiked = SoshageshinStorage.hasReacted(issueId, '\u2764\ufe0f');

    const bar = document.createElement('div');
    bar.className = 'like-section';
    bar.innerHTML = `
      <p class="like-section__text">\u3053\u306e\u65b0\u805e\u304c\u6c17\u306b\u5165\u3063\u305f\u3089<span class="like-section__highlight">\u3044\u3044\u306d</span>\u304a\u9858\u3044\u3057\u307e\u3059\uff01</p>
      <button class="like-section__btn ${hasLiked ? 'like-section__btn--active' : ''}" id="likeBtn">
        <span class="like-section__heart">\u2764\ufe0f</span>
      </button>
      <span class="like-section__count" id="likeCount">${likeCount > 0 ? likeCount : ''}</span>
    `;
    footer.parentNode.insertBefore(bar, footer);

    document.getElementById('likeBtn').addEventListener('click', function () {
        if (SoshageshinStorage.hasReacted(issueId, '\u2764\ufe0f')) return;
        const count = SoshageshinStorage.addReaction(issueId, '\u2764\ufe0f');
        SoshageshinStorage.markReacted(issueId, '\u2764\ufe0f');
        this.classList.add('like-section__btn--active');
        document.getElementById('likeCount').textContent = count;
        this.style.transform = 'scale(1.2)';
        setTimeout(() => this.style.transform = '', 300);
    });
}

function onReact() { /* Legacy — no longer used */ }

// ── SHARE BAR ──
function renderShareBar(title) {
    const footer = document.querySelector('.viewer-footer');
    if (!footer || typeof SoshageshinShare === 'undefined') return;

    const bar = document.createElement('div');
    bar.innerHTML = SoshageshinShare.buildShareBar(title, window.location.href);
    footer.parentNode.insertBefore(bar.firstElementChild, footer);
}

// ── SUMMARY (SEO text) ──
function renderSummary(meta) {
    if (!meta.summary && meta.tags.length === 0) return;
    const footer = document.querySelector('.viewer-footer');
    if (!footer) return;

    const section = document.createElement('div');
    section.className = 'viewer-summary';
    section.innerHTML = `
    <div class="viewer-summary__title">DISPATCH SUMMARY</div>
    <p>${meta.summary}</p>
    ${meta.tags.length ? `
      <div class="viewer-summary__tags">
        ${meta.tags.map(t => `<span class="tag-chip">${t}</span>`).join('')}
      </div>
    ` : ''}
  `;
    footer.parentNode.insertBefore(section, footer);
}

// ── COMMENTS (momon:GA style) ──
function renderComments(issueId) {
    const footer = document.querySelector('.viewer-footer');
    if (!footer) return;

    const section = document.createElement('div');
    section.className = 'comment-section';

    function formatDate(ts) {
        const d = new Date(ts);
        const pad = n => String(n).padStart(2, '0');
        return `${d.getFullYear()}/${pad(d.getMonth() + 1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
    }

    function buildCommentList(comments) {
        if (comments.length === 0) return '<p class="comment-section__empty">まだコメントはありません。最初のコメントを投稿しよう！</p>';
        return comments.map((c, i) => {
            const dateStr = formatDate(c.timestamp);
            const likes = SoshageshinStorage.getCommentLikes(issueId, i);
            const hasLiked = SoshageshinStorage.hasLikedComment(issueId, i);
            return `
                <div class="comment-item">
                    <div class="comment-item__header">
                        <span class="comment-item__num">${i + 1}.</span>
                        <span class="comment-item__name">${escapeHtml(c.name)}</span>
                        <span class="comment-item__time">${dateStr}</span>
                    </div>
                    <div class="comment-item__text">${escapeHtml(c.text)}</div>
                    <div class="comment-item__footer">
                        <button class="comment-item__like-btn${hasLiked ? ' liked' : ''}" data-idx="${i}">
                            👍
                        </button>
                        <span class="comment-item__like-count">${likes > 0 ? '+' + likes : ''}</span>
                    </div>
                </div>`;
        }).join('');
    }

    const comments = SoshageshinStorage.getComments(issueId);
    let collapsed = false;

    section.innerHTML = `
        <div class="comment-section__header">
            <div class="comment-section__title-area">
                <span class="comment-section__label">みんなの</span>
                <span class="comment-section__title">コメント</span>
            </div>
            <button class="comment-section__toggle" id="commentToggle">▸ コメントを非表示</button>
        </div>
        <div class="comment-section__body" id="commentBody">
            <div class="comment-section__list" id="commentList">
                ${buildCommentList(comments)}
            </div>
            <div class="comment-section__form">
                <div class="comment-section__form-row">
                    <input type="text" class="comment-section__name-input" id="commentName" placeholder="名前（空欄で「名無しの指揮官さん」）" maxlength="20">
                </div>
                <div class="comment-section__form-row">
                    <textarea class="comment-section__text-input" id="commentText" placeholder="コメントを入力..." maxlength="200" rows="3"></textarea>
                </div>
                <div class="comment-section__form-actions">
                    <span class="comment-section__count">${comments.length}件のコメント</span>
                    <button class="comment-section__submit" id="commentSubmit">送信</button>
                </div>
            </div>
        </div>
    `;

    footer.parentNode.insertBefore(section, footer);

    // Toggle visibility
    document.getElementById('commentToggle').addEventListener('click', () => {
        collapsed = !collapsed;
        const body = document.getElementById('commentBody');
        const btn = document.getElementById('commentToggle');
        body.style.display = collapsed ? 'none' : '';
        btn.textContent = collapsed ? '▸ コメントを表示' : '▸ コメントを非表示';
    });

    // Like handler (event delegation)
    document.getElementById('commentList').addEventListener('click', (e) => {
        const btn = e.target.closest('.comment-item__like-btn');
        if (!btn) return;
        const idx = parseInt(btn.dataset.idx);
        if (SoshageshinStorage.hasLikedComment(issueId, idx)) return;
        SoshageshinStorage.likeComment(issueId, idx);
        btn.classList.add('liked');
        const countEl = btn.nextElementSibling;
        const newCount = SoshageshinStorage.getCommentLikes(issueId, idx);
        countEl.textContent = '+' + newCount;
    });

    // Submit handler
    document.getElementById('commentSubmit').addEventListener('click', () => {
        const nameEl = document.getElementById('commentName');
        const textEl = document.getElementById('commentText');
        const text = textEl.value.trim();
        if (!text) return;

        const updated = SoshageshinStorage.addComment(issueId, nameEl.value.trim(), text);
        document.getElementById('commentList').innerHTML = buildCommentList(updated);
        section.querySelector('.comment-section__count').textContent = updated.length + '件のコメント';
        textEl.value = '';
    });

    // Enter to submit (Shift+Enter for newline)
    document.getElementById('commentText').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('commentSubmit').click();
        }
    });
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

function timeAgo(ts) {
    const diff = Date.now() - ts;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'たった今';
    if (mins < 60) return `${mins}分前`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}時間前`;
    const days = Math.floor(hrs / 24);
    return `${days}日前`;
}

// ── RELATED ISSUES (thumbnail gallery) ──
function renderRelated(meta) {
    if (typeof GAMES === 'undefined') return;
    const footer = document.querySelector('.viewer-footer');
    if (!footer) return;

    // Find games with matching tags, then fill with random
    let related = GAMES
        .filter(g => g.slug !== meta.gameSlug)
        .filter(g => g.latestIssue.tags && meta.tags.some(t => g.latestIssue.tags.includes(t)));

    // If not enough, fill with random games
    if (related.length < 6) {
        const existingSlugs = new Set(related.map(g => g.slug));
        const extra = GAMES
            .filter(g => g.slug !== meta.gameSlug && !existingSlugs.has(g.slug))
            .sort(() => Math.random() - 0.5);
        related = [...related, ...extra].slice(0, 6);
    } else {
        related = related.slice(0, 6);
    }

    if (related.length === 0) return;

    const section = document.createElement('div');
    section.className = 'related-section';
    section.innerHTML = `
    <div class="related-section__title">関連記事</div>
    <div class="related-grid">
      ${related.map(g => {
        const issue = g.latestIssue;
        const issueUrl = `../../../../games/${g.slug}/issues/${issue.date}/index.html`;
        return `
          <a class="related-thumb" href="${issueUrl}">
            <div class="related-thumb__cover">
              ${issue.thumbnail
                ? `<img src="../../../../${issue.thumbnail}" alt="${issue.title}" loading="lazy">`
                : `<div class="related-thumb__placeholder">${g.icon}</div>`
            }
            </div>
            <div class="related-thumb__info">
              <div class="related-thumb__game">${g.iconImage ? `<img src="../../../../${g.iconImage}" alt="" class="related-thumb__game-icon">` : ''} ${g.name}</div>
              <div class="related-thumb__title">${issue.title}</div>
            </div>
          </a>
        `;
    }).join('')}
    </div>
  `;
    footer.parentNode.insertBefore(section, footer);
}

// ── VIEWER APP BAR (scroll show/hide) ──
function initViewerAppBar() {
    const appBar = document.getElementById('viewerAppBar');
    if (!appBar) return;

    let lastScrollY = 0;
    let ticking = false;

    function onScroll() {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const currentY = window.scrollY;
                if (currentY < 60) {
                    // Near top: always show
                    appBar.classList.remove('app-bar--hidden');
                } else if (currentY > lastScrollY + 5) {
                    // Scrolling down: hide
                    appBar.classList.add('app-bar--hidden');
                } else if (currentY < lastScrollY - 5) {
                    // Scrolling up: show
                    appBar.classList.remove('app-bar--hidden');
                }
                lastScrollY = currentY;
                ticking = false;
            });
            ticking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });
}

// ── VIEWER HAMBURGER MENU ──
function initViewerMenu() {
    const btn = document.getElementById('hamburgerBtn');
    const menu = document.getElementById('slideMenu');
    const overlay = document.getElementById('menuOverlay');
    const closeBtn = document.getElementById('menuClose');
    const gameList = document.getElementById('menuGameList');

    if (!btn || !menu) return;

    function openMenu() {
        menu.classList.add('open');
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        menu.classList.remove('open');
        overlay.classList.remove('open');
        document.body.style.overflow = '';
    }

    btn.addEventListener('click', openMenu);
    if (overlay) overlay.addEventListener('click', closeMenu);
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);

    menu.querySelectorAll('.slide-menu__link').forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    // Populate game list sorted by latest issue date (newest first)
    if (gameList && typeof GAMES !== 'undefined') {
        const sorted = [...GAMES].sort((a, b) =>
            b.latestIssue.date.localeCompare(a.latestIssue.date)
        );
        gameList.innerHTML = sorted.map(g => `
          <a class="slide-menu__game" href="../../../../games/${g.slug}/index.html">
            <span class="slide-menu__game-icon">${g.iconImage ? `<img src="../../../../${g.iconImage}" alt="">` : g.icon}</span>
            <span class="slide-menu__game-name">${g.name}</span>
          </a>
        `).join('');
    }
}

// ── VIEWER SEARCH (popup style) ──
function initViewerSearch() {
    const searchBtn = document.getElementById('searchBtn');
    const overlay = document.getElementById('searchOverlay');
    const input = document.getElementById('searchInput');
    const closeBtn = document.getElementById('searchClose');
    const results = document.getElementById('searchResults');

    if (!searchBtn || !overlay) return;

    function openSearch() {
        overlay.classList.add('open');
        document.body.style.overflow = 'hidden';
        setTimeout(() => input && input.focus(), 100);
    }

    function closeSearch() {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
        if (input) input.value = '';
        if (results) results.innerHTML = '';
    }

    function performSearch() {
        const q = input.value.trim().toLowerCase();
        if (q.length === 0 || typeof GAMES === 'undefined') {
            results.innerHTML = '';
            return;
        }

        // 1) Game name matches → link to game list page
        const gameMatches = GAMES.filter(g => {
            const nameSearch = [g.name, g.nameEn || '', g.slug].join(' ').toLowerCase();
            return nameSearch.includes(q);
        });

        // 2) Article/keyword matches → link to issue page
        const articleMatches = GAMES.filter(g => {
            const articleSearch = [
                g.latestIssue.title, g.latestIssue.summary || '',
                ...(g.latestIssue.tags || []), g.genre
            ].join(' ').toLowerCase();
            return articleSearch.includes(q);
        });

        if (gameMatches.length === 0 && articleMatches.length === 0) {
            results.innerHTML = '<p class="search-popup__empty">見つかりませんでした</p>';
            return;
        }

        let html = '';

        // Game name suggestions
        if (gameMatches.length > 0) {
            html += '<div class="search-section">';
            html += '<div class="search-section__label">🎮 ゲーム一覧</div>';
            html += gameMatches.slice(0, 8).map(g => `
              <a class="search-result search-result--game" href="../../../../games/${g.slug}/index.html">
                <span class="search-result__icon">${g.iconImage ? `<img src="../../../../${g.iconImage}" alt="">` : g.icon}</span>
                <div class="search-result__body">
                  <div class="search-result__name">${g.name}</div>
                  <div class="search-result__sub">記事一覧を見る →</div>
                </div>
              </a>
            `).join('');
            html += '</div>';
        }

        // Article matches
        if (articleMatches.length > 0) {
            html += '<div class="search-section">';
            html += '<div class="search-section__label">📰 記事</div>';
            html += articleMatches.slice(0, 10).map(g => `
              <a class="search-result" href="../../../../games/${g.slug}/issues/${g.latestIssue.date}/index.html">
                <span class="search-result__icon">${g.iconImage ? `<img src="../../../../${g.iconImage}" alt="">` : g.icon}</span>
                <div class="search-result__body">
                  <div class="search-result__name">${g.name}</div>
                  <div class="search-result__title">${g.latestIssue.title}</div>
                </div>
              </a>
            `).join('');
            html += '</div>';
        }

        results.innerHTML = html;
    }

    searchBtn.addEventListener('click', openSearch);
    if (closeBtn) closeBtn.addEventListener('click', closeSearch);

    // Click on overlay bg to close
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeSearch();
    });

    // Live search on input
    if (input && results) {
        input.addEventListener('input', performSearch);

        // Enter key also triggers search
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }

    // ESC to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('open')) closeSearch();
    });
}

