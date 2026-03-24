import { ContextRegistry } from '/static/js/core/ContextRegistry.js';
import { SubmitFormBinder } from '/static/js/binders/submitFormBinder.js';
import { SaveChangeFormBinder } from '/static/js/pages/round_table/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/round_table/binders/setActionBinder.js';


const ctx = {
    ctxName: 'round_table',
    tabName: 'form_round_table',
    contentSelector: 'contentTab',
    binders: new Map(),
    initiators: new Map(),
    // --- Методы биндеров ---
    registerBinders(tabName, binders) { ctx.binders.set(tabName, binders); },
    getCurrentBinders() { return this.binders.get(this.tabName) || []; },
    // --- Методы инициаторов --- 
    registerInitiator(tabName, fn) { this.initiators.set(tabName, fn); }, 
    getInitiator() { return this.initiators.get(this.tabName) || (() => {}); },
    // Метоты состояния
    setTabName(name){ this.tabName = name; },
    getTabName(){ return this.tabName; },
    getContentSelector(){ return ctx.contentSelector; }
};

const round_table_binders = [SubmitFormBinder];
ctx.registerBinders('form_round_table', round_table_binders);

const list_protocols_binders = [SaveChangeFormBinder, SetActionBinder];
ctx.registerBinders('report_round_table', list_protocols_binders);

// РЕГИСТРАЦИЯ 
ContextRegistry.register(ctx.ctxName, ctx);
