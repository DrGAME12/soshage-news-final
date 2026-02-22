// ============================================================
//  SOSHAGESHIN — SNS Share Utilities
// ============================================================

const SoshageshinShare = {
    twitter(text, url) {
        const params = new URLSearchParams({ text, url });
        window.open(`https://twitter.com/intent/tweet?${params}`, '_blank', 'width=550,height=420');
    },

    line(text, url) {
        const msg = encodeURIComponent(`${text}\n${url}`);
        window.open(`https://social-plugins.line.me/lineit/share?text=${msg}`, '_blank');
    },

    // Copy link to clipboard
    async copyLink(url) {
        try {
            await navigator.clipboard.writeText(url || window.location.href);
            return true;
        } catch {
            // Fallback
            const ta = document.createElement('textarea');
            ta.value = url || window.location.href;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            return true;
        }
    },

    // Build share bar HTML
    buildShareBar(title, url) {
        return `
      <div class="share-bar">
        <span class="share-bar__label">SHARE</span>
        <button class="share-bar__btn share-bar__btn--x" onclick="SoshageshinShare.twitter('${title.replace(/'/g, "\\'")}', '${url || window.location.href}')" title="Xでシェア">𝕏</button>
        <button class="share-bar__btn share-bar__btn--line" onclick="SoshageshinShare.line('${title.replace(/'/g, "\\'")}', '${url || window.location.href}')" title="LINEでシェア">LINE</button>
        <button class="share-bar__btn share-bar__btn--copy" onclick="SoshageshinShare.copyLink().then(()=>this.textContent='✓')" title="リンクコピー">🔗</button>
      </div>
    `;
    }
};
