// ============================================================
//  SOSHAGESHIN — Theme Toggle (Dark / Light)
// ============================================================

(function initTheme() {
    const saved = SoshageshinStorage.getTheme();
    document.documentElement.setAttribute('data-theme', saved);
})();

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    SoshageshinStorage.setTheme(next);

    // Update toggle button icon
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = next === 'dark' ? '☀️' : '🌙';
}
