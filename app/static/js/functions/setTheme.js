export function setTheme() {
    const html = document.documentElement;
    const icon = document.getElementById("theme-icon");
    if (!icon) return;

    function updateIcon() {
        icon.src =
            html.dataset.theme === "dark"
                ? "/static/img/color-icon.png"
                : "/static/img/dark-icon.png";
    }

    updateIcon();

    window.toggleTheme = function () {
        const newTheme = html.dataset.theme === "dark" ? "color" : "dark";
        html.dataset.theme = newTheme;
        localStorage.setItem("theme", newTheme);
        updateIcon();
    };
}
