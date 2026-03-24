function toggleTheme() {
    const html = document.documentElement;
    const current = html.dataset.theme || 'color';
    const next = current === 'color' ? 'dark' : 'color';

    html.dataset.theme = next;
    localStorage.setItem('theme', next);
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    btn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
    });
});
