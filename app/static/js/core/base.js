function applyTheme(theme) {
    const html = document.documentElement;
    const icon = document.getElementById('theme-toggle');

    html.dataset.theme = theme;

    icon.textContent = theme === 'color' ? '🌙' : '☀️';
}


function toggleTheme() {
    const html = document.documentElement;
    const current = html.dataset.theme || 'color';
    const next = current === 'color' ? 'dark' : 'color';

    localStorage.setItem('theme', next);
    applyTheme(next);
}

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    // восстановление темы при загрузке
    const saved = localStorage.getItem('theme') || 'color';
    applyTheme(saved);

    btn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleTheme();
    });
});
