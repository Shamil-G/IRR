export function serializeParams(params) {
    const isJson = Object.values(params).some(v => typeof v === 'object' && v !== null);

    const headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': isJson ? 'application/json' : 'application/x-www-form-urlencoded'
    };

    const body = isJson
        ? JSON.stringify(params)
        : new URLSearchParams(params).toString();

    return { headers, body };
}

export const SaveChangeFormBinder = {
    role: 'save-change-form',

    attach(button) {
        if (button.__saveChangeFormBound) return;
        button.__saveChangeFormBound = true;

        button.addEventListener('change', (e) => {
            const value = button.value;

            if (!value) {
                console.error('SaveChangeFormBinder: Input has no value');
                return;
            }

            // ѕросто редиректим на страницу с параметром
            window.location.href = `/meet/protocol?period=${encodeURIComponent(value)}`;
        });
    },

    attachAll(zone = document) {
        const buttons = zone.querySelectorAll(`[data-role="${this.role}"]`);
        buttons.forEach(btn => this.attach(btn));
    }
};