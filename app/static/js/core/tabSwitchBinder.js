import { FragmentLoadAndBind } from '/static/js/core/FragmentLoader.js'
import { ContextRegistry } from '/static/js/core/ContextRegistry.js';

export async function loadTabContent(ctxName, extraParams = {} ) {
    const ctx = ContextRegistry.get(ctxName);
    
    console.log('TabSwitchBinder. ctxName: ', ctxName, '\ntabName: ', ctx.getTabName(),'\nctx: ', ctx);

    const targetSelector = ctx.getContentSelector();
    const targetId = targetSelector.replace('#', '');

    await FragmentLoadAndBind(
        '/get_fragment',
        targetId,
        {
            fragment: ctx.getTabName(),
            ...extraParams
        },
        ctxName,
        (html, target) => {}
    );
}

export const TabSwitchBinder = {
    // role: 'tab-switch',
    // massive: true,

    // ------------------------------------------------------------
    // 2. КОНТЕНТ ТАБОВ
    // ------------------------------------------------------------
    attach(button, tabZone, ctxName) {
        button.addEventListener('click', () => {
            console.log('TabSwitchBinder. addEventListener on ', tabZone);
            const tabName = button.dataset.tab;
            if (!tabName) return;
            const activeTab = tabZone.querySelector('.active');
            if (activeTab){
               activeTab.classList.remove('active');
            };
            button.classList.add('active');
            //console.log('TabSwitchBinder. active: ', button, ', passive: ', activeTab);

            // 4. Запоминаем таб
            const ctx = ContextRegistry.get(ctxName);
            ctx.setTabName(tabName);

            // 5. Загружаем контент
            loadTabContent(ctxName);
        });
    },

    attachAll(tabZone = document, ctxName) {
        if (!tabZone) {
            console.warn('TabSwitchBinder: tabZone не передан');
            return;
        }
        //const buttons = tabZone.querySelectorAll('button[data-tab]');

        const buttons = Array.from(
            tabZone.querySelectorAll('button[data-tab]')
        );
        buttons.forEach(btn => this.attach(btn, tabZone, ctxName));
    }
};
