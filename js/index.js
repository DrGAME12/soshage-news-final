// ============================================================
//  SOSHAGESHIN — Top Page (Index)
//  Gallery grid with thumbnail covers, tags, history, bookmarks
// ============================================================


// Pinned games appear first in recommendations
const PINNED_SLUGS = [
  'hunter', 'fanpare',
  'blue-archive', 'nikke', 'wuthering-waves', 'version64', 'starrail',
  'heban', 'project-sekai', 'umamusume',
  'arkknights', 'ggene-eternal'
];

document.addEventListener('DOMContentLoaded', () => {
  renderDate();
  renderHistory();
  renderRecommendations();
  renderDispatchGallery();
  renderTrending();
  renderRanking();
  initHamburgerMenu();
  initSearch();
});

function renderDate() {
  const d = new Date();
  const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
  const el = document.getElementById('currentDate');
  if (el) el.textContent =
    `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} [${days[d.getDay()]}]`;
}

// ────────────────────────────────────────────
//  HISTORY STRIP (最近読んだ号)
// ────────────────────────────────────────────
function renderHistory() {
  const section = document.getElementById('historySection');
  const strip = document.getElementById('historyStrip');
  if (!section || !strip) return;

  const hist = SoshageshinStorage.getHistory();
  if (hist.length === 0) { section.style.display = 'none'; return; }

  section.style.display = '';
  strip.innerHTML = hist.slice(0, 6).map(h => `
    <a class="history-chip" href="${h.path}">
      <span class="history-chip__game">${h.game}</span>
      <span class="history-chip__title">${h.title}</span>
      <span class="history-chip__date">${h.date}</span>
    </a>
  `).join('');
}

// ────────────────────────────────────────────
//  RECOMMENDATIONS (あなたへのおすすめ)
//  Smart picks: bookmarked games first, then new unread, then popular
// ────────────────────────────────────────────
function renderRecommendations() {
  const feed = document.getElementById('recommendFeed');
  if (!feed) return;

  // ── Pick logic ──
  // 0) Pinned games (always first)  1) Bookmarked + unread  2) Bookmarked + read  3) New unread  4) Random fill
  const pinnedGames = PINNED_SLUGS.map(slug => GAMES.find(g => g.slug === slug)).filter(Boolean);
  const bookmarked = GAMES.filter(g => SoshageshinStorage.isBookmarked(g.slug) && !PINNED_SLUGS.includes(g.slug));
  const others = GAMES.filter(g => !SoshageshinStorage.isBookmarked(g.slug) && !PINNED_SLUGS.includes(g.slug));

  const bmUnread = bookmarked.filter(g => !SoshageshinStorage.isRead(`${g.slug}_${g.latestIssue.date}`));
  const bmRead = bookmarked.filter(g => SoshageshinStorage.isRead(`${g.slug}_${g.latestIssue.date}`));
  const newUnread = others.filter(g => !SoshageshinStorage.isRead(`${g.slug}_${g.latestIssue.date}`));
  const rest = others.filter(g => SoshageshinStorage.isRead(`${g.slug}_${g.latestIssue.date}`));

  let picks = [];
  const addPick = (g, reason) => { if (picks.length < 12) picks.push({ game: g, reason }); };

  // Pinned games always appear first
  pinnedGames.forEach(g => addPick(g, '📌 注目'));

  bmUnread.forEach(g => addPick(g, '⭐ お気に入り・未読'));
  bmRead.forEach(g => addPick(g, '⭐ お気に入り'));
  newUnread.sort(() => Math.random() - 0.5).forEach(g => addPick(g, '🆕 NEW'));

  // Fill remaining with random unseen
  if (picks.length < 12) {
    const remaining = rest.filter(g => !picks.find(p => p.game.slug === g.slug));
    remaining.sort(() => Math.random() - 0.5);
    remaining.forEach(g => addPick(g, '📰 おすすめ'));
  }

  // Final random fill from all if still short
  if (picks.length < 12) {
    const used = new Set(picks.map(p => p.game.slug));
    const allRemaining = GAMES.filter(g => !used.has(g.slug));
    allRemaining.sort(() => Math.random() - 0.5);
    allRemaining.forEach(g => addPick(g, '📰 おすすめ'));
  }

  picks = picks.slice(0, 12);

  feed.innerHTML = picks.map(({ game: g, reason }) => {
    const issue = g.latestIssue;
    const issueUrl = `games/${g.slug}/issues/${issue.date}/index.html`;

    return `
      <a class="recommend-card" href="${issueUrl}" style="--accent: ${g.color}">
        <div class="recommend-card__cover">
          ${issue.thumbnail
        ? `<img src="${issue.thumbnail}" alt="${issue.title}" loading="lazy">`
        : `<div class="recommend-card__placeholder">${g.icon}</div>`
      }
          <span class="recommend-card__reason">${reason}</span>
        </div>
        <div class="recommend-card__info">
          <div class="recommend-card__game">
            ${g.iconImage ? `<img src="${g.iconImage}" alt="" class="recommend-card__game-icon">` : ''}
            ${g.name}
          </div>
          <div class="recommend-card__title">${issue.title}</div>
          <div class="recommend-card__date">📅 ${issue.date.replace(/-/g, '年').replace(/年(\d{2})$/, '月$1日')}</div>
        </div>
      </a>
    `;
  }).join('');
}


// ────────────────────────────────────────────
//  DISPATCH GALLERY — 2-column thumbnail grid
//  (manga gallery style: big cover image + title + date + likes)
// ────────────────────────────────────────────
function renderDispatchGallery() {
  const feed = document.getElementById('dispatchFeed');

  let items = [...GAMES].sort((a, b) =>
    b.latestIssue.date.localeCompare(a.latestIssue.date)
  );
  if (items.length === 0) {
    feed.innerHTML = '<p class="empty-message">該当する戦報はありません</p>';
    return;
  }

  feed.innerHTML = items.map(g => {
    const issue = g.latestIssue;
    const issueId = `${g.slug}_${issue.date}`;
    const issueUrl = `games/${g.slug}/issues/${issue.date}/index.html`;
    const reactions = SoshageshinStorage.getReactions(issueId);
    const likeCount = Object.values(reactions).reduce((sum, n) => sum + n, 0);
    const isNew = !SoshageshinStorage.isRead(issueId);

    return `
      <a class="gallery-card" href="${issueUrl}" style="--accent: ${g.color}">
        <div class="gallery-card__cover">
          ${issue.thumbnail
        ? `<img src="${issue.thumbnail}" alt="${issue.title}" loading="lazy">`
        : `<div class="gallery-card__placeholder">${g.icon}</div>`
      }
          ${isNew ? '<span class="gallery-card__new">NEW</span>' : ''}
          <div class="gallery-card__likes">
            <span class="gallery-card__heart">❤</span> ${likeCount}+
          </div>
        </div>
        <div class="gallery-card__info">
          <div class="gallery-card__title">${issue.title}</div>
          <div class="gallery-card__meta">
            <span class="gallery-card__game">${g.iconImage ? `<img src="${g.iconImage}" alt="" class="gallery-card__game-icon">` : g.icon} ${g.name}</span>
          </div>
          <div class="gallery-card__date">📅 ${issue.date.replace(/-/g, '年').replace(/年(\d{2})$/, '月$1日')}</div>
        </div>
      </a>
    `;
  }).join('');
}

// ────────────────────────────────────────────
//  TRENDING (急上昇 — recent + high engagement)
// ────────────────────────────────────────────
function renderTrending() {
  const list = document.getElementById('trendingList');
  if (!list) return;

  const now = Date.now();
  const scored = GAMES.map(g => {
    const issue = g.latestIssue;
    const issueId = `${g.slug}_${issue.date}`;
    const reactions = SoshageshinStorage.getReactions(issueId);
    const likeCount = Object.values(reactions).reduce((sum, n) => sum + n, 0);
    const daysSince = Math.max(1, (now - new Date(issue.date).getTime()) / 86400000);
    // Score: recency weight + engagement
    const score = likeCount / daysSince + (1 / daysSince) * 10;
    return { game: g, score, likeCount };
  }).sort((a, b) => b.score - a.score).slice(0, 6);

  if (scored.length === 0) {
    list.innerHTML = '<p class="empty-message">データがありません</p>';
    return;
  }

  list.innerHTML = '<div class="dispatch-feed">' + scored.map(({ game: g, likeCount }) => {
    const issue = g.latestIssue;
    const issueUrl = `games/${g.slug}/issues/${issue.date}/index.html`;
    const isNew = !SoshageshinStorage.isRead(`${g.slug}_${issue.date}`);

    return `
      <a class="gallery-card" href="${issueUrl}" style="--accent: ${g.color}">
        <div class="gallery-card__cover">
          ${issue.thumbnail
        ? `<img src="${issue.thumbnail}" alt="${issue.title}" loading="lazy">`
        : `<div class="gallery-card__placeholder">${g.icon}</div>`
      }
          ${isNew ? '<span class="gallery-card__new">NEW</span>' : ''}
          <div class="gallery-card__likes">
            <span class="gallery-card__heart">❤</span> ${likeCount}+
          </div>
        </div>
        <div class="gallery-card__info">
          <div class="gallery-card__title">${issue.title}</div>
          <div class="gallery-card__meta">
            <span class="gallery-card__game">${g.iconImage ? `<img src="${g.iconImage}" alt="" class="gallery-card__game-icon">` : g.icon} ${g.name}</span>
          </div>
        </div>
      </a>
    `;
  }).join('') + '</div>';
}

// ────────────────────────────────────────────
//  RANKING (based on localStorage read count)
// ────────────────────────────────────────────
function renderRanking() {
  const list = document.getElementById('rankingList');
  if (!list) return;

  const hist = SoshageshinStorage.getHistory();
  const counts = {};
  hist.forEach(h => {
    counts[h.id] = counts[h.id] || { ...h, count: 0 };
    counts[h.id].count++;
  });

  const ranked = Object.values(counts)
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  if (ranked.length === 0) {
    list.innerHTML = '<p class="empty-message">まだ閲覧データがありません</p>';
    return;
  }

  list.innerHTML = ranked.map((r, i) => `
    <a class="ranking-item" href="${r.path}">
      <span class="ranking-item__rank">#${i + 1}</span>
      <div class="ranking-item__body">
        <div class="ranking-item__title">${r.title}</div>
        <span class="ranking-item__game">${r.game}</span>
      </div>
      <span class="ranking-item__count">${r.count}回閲覧</span>
    </a>
  `).join('');
}

// ────────────────────────────────────────────
//  HAMBURGER MENU
// ────────────────────────────────────────────
function initHamburgerMenu() {
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
  overlay.addEventListener('click', closeMenu);
  closeBtn.addEventListener('click', closeMenu);

  // Close on nav link click
  menu.querySelectorAll('.slide-menu__link').forEach(link => {
    link.addEventListener('click', closeMenu);
  });

  // Populate game list sorted by latest issue date (newest first)
  if (gameList) {
    const sorted = [...GAMES].sort((a, b) =>
      b.latestIssue.date.localeCompare(a.latestIssue.date)
    );
    gameList.innerHTML = sorted.map(g => `
      <a class="slide-menu__game" href="games/${g.slug}/index.html">
        <span class="slide-menu__game-icon">${g.iconImage ? `<img src="${g.iconImage}" alt="">` : g.icon}</span>
        <span class="slide-menu__game-name">${g.name}</span>
      </a>
    `).join('');
  }
}

// ────────────────────────────────────────────
//  SEARCH OVERLAY
// ────────────────────────────────────────────
function initSearch() {
  const searchBtn = document.getElementById('searchBtn');
  const overlay = document.getElementById('searchOverlay');
  const input = document.getElementById('searchInput');
  const closeBtn = document.getElementById('searchClose');
  const results = document.getElementById('searchResults');

  if (!searchBtn || !overlay) return;

  function openSearch() {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    setTimeout(() => input.focus(), 100);
  }

  function closeSearch() {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
    input.value = '';
    results.innerHTML = '';
  }

  function performSearch() {
    const q = input.value.trim().toLowerCase();
    if (q.length === 0) {
      results.innerHTML = '';
      return;
    }

    // 1) Game name matches (name/nameEn/slug match) → link to game list page
    const gameMatches = GAMES.filter(g => {
      const nameSearch = [g.name, g.nameEn || '', g.slug].join(' ').toLowerCase();
      return nameSearch.includes(q);
    });

    // 2) Article/keyword matches (title, summary, tags, genre) → link to issue page
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

    // Game name suggestions section
    if (gameMatches.length > 0) {
      html += '<div class="search-section">';
      html += '<div class="search-section__label">🎮 ゲーム一覧</div>';
      html += gameMatches.slice(0, 8).map(g => `
        <a class="search-result search-result--game" href="games/${g.slug}/index.html">
          <span class="search-result__icon">${g.iconImage ? `<img src="${g.iconImage}" alt="">` : g.icon}</span>
          <div class="search-result__body">
            <div class="search-result__name">${g.name}</div>
            <div class="search-result__sub">記事一覧を見る →</div>
          </div>
        </a>
      `).join('');
      html += '</div>';
    }

    // Article matches section
    if (articleMatches.length > 0) {
      html += '<div class="search-section">';
      html += '<div class="search-section__label">📰 記事</div>';
      html += articleMatches.slice(0, 10).map(g => `
        <a class="search-result" href="games/${g.slug}/issues/${g.latestIssue.date}/index.html">
          <span class="search-result__icon">${g.iconImage ? `<img src="${g.iconImage}" alt="">` : g.icon}</span>
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
  closeBtn.addEventListener('click', closeSearch);

  // Click on overlay bg to close
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeSearch();
  });

  // Live search on input
  input.addEventListener('input', performSearch);

  // Enter key also triggers search
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      performSearch();
    }
  });

  // ESC to close
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('open')) closeSearch();
  });
}
