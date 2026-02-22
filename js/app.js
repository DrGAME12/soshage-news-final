// ============================================================
//  SOSHAGESHIN — Rendering Engine
//  Transforms structured data into military newspaper DOM
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  renderMasthead();
  renderTopNews();
  renderUnitIntel();
  renderCommunityPulse();
  renderOpsSchedule();
  initScrollAnimations();
});

// ────────────────────────────────────────────
//  MASTHEAD
// ────────────────────────────────────────────
function renderMasthead() {
  const m = PATCH_DATA.meta;
  document.getElementById('classification').textContent = m.classification;
  document.getElementById('mastheadTitle').textContent = m.title;
  document.getElementById('mastheadSubtitle').textContent = m.subtitle;
  document.getElementById('metaEdition').textContent = m.edition;
  document.getElementById('metaDate').textContent = formatDate(m.date);
  document.getElementById('metaCodename').textContent = m.codename;
}

// ────────────────────────────────────────────
//  CSS BANNER BUILDER (image replacement)
// ────────────────────────────────────────────
function buildSectionBanner(icon, title, subtitle, modifier) {
  return `
    <div class="section-banner section-banner--${modifier}">
      <div class="section-banner__icon">${icon}</div>
      <div class="section-banner__text">
        <div class="section-banner__title">${title}</div>
        <div class="section-banner__subtitle">${subtitle}</div>
      </div>
      <div class="section-banner__grid"></div>
    </div>
  `;
}

// ────────────────────────────────────────────
//  SECTION 1: Top Strategic News
// ────────────────────────────────────────────
function renderTopNews() {
  const d = PATCH_DATA.topNews;
  const container = document.getElementById('topNewsContent');

  const keyPointsHtml = d.keyPoints.map(kp =>
    `<li>${escapeHtml(kp)}</li>`
  ).join('');

  container.innerHTML = `
    ${buildSectionBanner('⚔️', 'STRATEGIC BRIEFING', 'OPERATION CRIMSON VIPER — PRIORITY ALPHA', 'topnews')}
    <h3 class="top-news__headline">${escapeHtml(d.headline)}</h3>
    <p class="top-news__subhead">${escapeHtml(d.subhead)}</p>
    <p class="top-news__body">${escapeHtml(d.summary)}</p>
    <ul class="top-news__keypoints">${keyPointsHtml}</ul>
    ${buildPromptToggle(d.imagePrompt)}
  `;
}

// ────────────────────────────────────────────
//  SECTION 2: Unit Intel
// ────────────────────────────────────────────
function renderUnitIntel() {
  const units = PATCH_DATA.unitIntel;
  const container = document.getElementById('unitIntelContent');

  const cardsHtml = units.map(u => {
    const beforeStats = formatStats(u.before);
    const afterStats = formatStats(u.after);

    return `
      <div class="unit-card">
        <div class="unit-card__header">
          <div>
            <span class="unit-card__name">${escapeHtml(u.unitName)}</span>
            <span class="unit-card__role"> ─ ${escapeHtml(u.role)}</span>
          </div>
          <span class="unit-card__tag unit-card__tag--${u.changeType}">${u.changeType.toUpperCase()}</span>
        </div>
        <div class="unit-card__body">
          <div class="unit-card__comparison">
            <div class="unit-card__col unit-card__col--before">
              <span class="unit-card__col-label unit-card__col-label--before">BEFORE</span>
              ${beforeStats}
            </div>
            <div class="unit-card__col unit-card__col--after">
              <span class="unit-card__col-label unit-card__col-label--after">AFTER</span>
              ${afterStats}
            </div>
          </div>
          <div class="unit-card__eval">${escapeHtml(u.tacticalEval)}</div>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    ${buildSectionBanner('🔧', 'UNIT ANALYSIS', 'BALANCE ADJUSTMENT SUMMARY — FIELD REPORT', 'unitintel')}
    ${cardsHtml}
    ${buildPromptToggle(PATCH_DATA.unitIntelImagePrompt)}
  `;
}

function formatStats(stats) {
  return `
    HP: ${stats.hp.toLocaleString()}<br>
    装甲: ${stats.armor}<br>
    速度: ${stats.speed}<br>
    ${escapeHtml(stats.skill)}
  `;
}

// ────────────────────────────────────────────
//  SECTION 3: Community Pulse
// ────────────────────────────────────────────
function renderCommunityPulse() {
  const logs = PATCH_DATA.communityPulse;
  const container = document.getElementById('communityPulseContent');

  const logsHtml = logs.map(l => `
    <div class="comms__log">
      <div class="comms__log-header">
        <span>
          <span class="comms__sentiment comms__sentiment--${l.sentiment}"></span>
          <span class="comms__callsign">${escapeHtml(l.callsign)}</span>
          <span class="comms__affiliation">/ ${escapeHtml(l.affiliation)}</span>
        </span>
        <span class="comms__timestamp">${escapeHtml(l.timestamp)}</span>
      </div>
      <div class="comms__message">${escapeHtml(l.message)}</div>
    </div>
  `).join('');

  container.innerHTML = `
    ${buildSectionBanner('📡', 'SIGINT INTERCEPT', 'UNENCRYPTED COMMS — VERIFICATION COMPLETE', 'comms')}
    <p class="comms__intro">[SIGINT] 以下は各戦域通信網より傍受された非暗号化通信の抜粋である。発信者の特定・検証は完了済み。</p>
    ${logsHtml}
    ${buildPromptToggle(PATCH_DATA.communityPulseImagePrompt)}
  `;
}

// ────────────────────────────────────────────
//  SECTION 4: Operational Schedule
// ────────────────────────────────────────────
function renderOpsSchedule() {
  const ops = PATCH_DATA.operationalSchedule;
  const container = document.getElementById('opsScheduleContent');

  const itemsHtml = ops.map(o => `
    <li class="ops__item">
      <div class="ops__date">
        <span class="ops__date-label">${escapeHtml(o.dateLabel)}</span>
        ${escapeHtml(o.date)}
      </div>
      <div class="ops__event">
        ${escapeHtml(o.event)}
        <span class="ops__time">${escapeHtml(o.time)}</span>
      </div>
      <span class="ops__priority ops__priority--${o.priority}">${o.priority}</span>
    </li>
  `).join('');

  container.innerHTML = `
    ${buildSectionBanner('📋', 'OPS CALENDAR', 'UPCOMING OPERATIONS — TIMELINE OVERVIEW', 'ops')}
    <ul class="ops__list">${itemsHtml}</ul>
    ${buildPromptToggle(PATCH_DATA.operationalScheduleImagePrompt)}
  `;
}

// ────────────────────────────────────────────
//  SCROLL ANIMATION (IntersectionObserver)
// ────────────────────────────────────────────
function initScrollAnimations() {
  const sections = document.querySelectorAll('.section');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.08,
    rootMargin: '0px 0px -40px 0px'
  });

  sections.forEach(section => observer.observe(section));
}

// ────────────────────────────────────────────
//  PROMPT TOGGLE (折りたたみ)
// ────────────────────────────────────────────
function buildPromptToggle(prompt) {
  const id = 'prompt_' + Math.random().toString(36).substr(2, 8);
  return `
    <div class="prompt-toggle">
      <button class="prompt-toggle__btn" onclick="togglePrompt('${id}')">
        📡 IMAGE GEN PROMPT
      </button>
      <div class="prompt-toggle__content" id="${id}">
        <div class="prompt-toggle__text">${escapeHtml(prompt)}</div>
      </div>
    </div>
  `;
}

function togglePrompt(id) {
  const el = document.getElementById(id);
  el.classList.toggle('is-open');
}

// ────────────────────────────────────────────
//  UTILITIES
// ────────────────────────────────────────────
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} [${days[d.getDay()]}]`;
}
