// Универсальные функции для загрузки любых фрагментов 
// fragmentLoader.js
import { ContextRegistry } from '/static/js/core/ContextRegistry.js';

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

export function fadeInsert(root) {
    // Сбрасываем возможные предыдущие стили
    root.style.transition = 'none';
    root.style.opacity = 0;

    // Даем браузеру один кадр, чтобы применить opacity: 0
    requestAnimationFrame(() => {
        root.style.transition = 'opacity 0.25s ease';
        root.style.opacity = 1;

        // Чистим transition после завершения
        setTimeout(() => {
            root.style.transition = '';
        }, 200);
    });
}

export async function FragmentLoad(url, targetId, params = {}, onLoaded = null) {
    const target = document.getElementById(targetId);
    console.log('--- FragmentLoad\n\turl:', url, '\n\tparams: ', params, '\n\ttargetId: ', targetId, '\n\tonLoaded: ', onLoaded,'\n\ttarget: ', target);
    if (!target) return;

    const { headers, body } = serializeParams(params);

    try {
        //console.log('--- FragmentLoad\n\ttry fetch');
        const res = await fetch(url, { method: 'POST', headers, body });
        const html = await res.text();

        // Вставляем HTML
        target.innerHTML = html;

        //console.log('--- FragmentLoad\n\thtml:', html);

        // Плавный fade-in
        fadeInsert(target);

        console.log('--- FragmentLoad\n\tonLoaded. Target', target);
        if (onLoaded) onLoaded(html, target);
        //console.log('--- FragmentLoad Finish');

    } catch (err) {
        console.error('FragmentLoad\nonLoaded', onLoaded, '\nerror:', err);
    }
}

// --- 2. Загрузка + биндеры (универсальная) ---
export async function FragmentLoadAndBind(
    url,
    targetId,
    params = {},
    ctxName,
    onLoaded = null
) {
    //console.log('*** FragmentLoadandBind\n\turl:', url, '\n\tparams: ', params, '\n\ttargetId: ', targetId);
    await FragmentLoad(url, targetId, params, (html, target) => {
        //console.log('--- FragmentLoadandBind\n\turl:', url, '\n\tparams: ', params, '\n\ttargetId: ',targetId, '\n\tbinders: ', binders);
        const ctx = ContextRegistry.get(ctxName);
        if(!ctx){
            console.error('FragmentLoadAndBind: ctx not found for', ctxName); 
            return;
        }
        
        // 1. Биндеры
        const binders = ctx.getCurrentBinders();
        console.log('FragmentLoad. \ncxtName: ',ctxName,'\ntarget: ', target, '\n\tbinders: ', binders);
        binders.forEach(b => b.attachAll(target));
        // 2. Функции инициаторы
        const init = ctx.getInitiator(); 
        if(init) init(target);
        
        if (onLoaded) onLoaded(html, target);
    });
}


