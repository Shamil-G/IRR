// ctxState_protocols.js 
import { ContextRegistry } from '/static/js/core/ContextRegistry.js';
import { SaveChangeFormBinder } from '/static/js/pages/protocols/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/protocols/binders/setActionBinder.js';


// ctxState.js
const ctx = {
    ctxName: 'protocols',
    tabName: 'meet_labor',
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

const list_protocols_binders = [SaveChangeFormBinder, SetActionBinder];

ctx.registerBinders('list_protocols', list_protocols_binders);


// РЕГИСТРАЦИЯ 
ContextRegistry.register(ctx.ctxName, ctx);
