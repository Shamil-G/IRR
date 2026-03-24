import { ContextRegistry } from '/static/js/core/ContextRegistry.js';
import { SubmitFormBinder } from '/static/js/binders/submitFormBinder.js';
import { SetActionBinder } from '/static/js/pages/print_smi/binders/setActionBinder.js';
import { SaveChangeFormBinder } from '/static/js/pages/print_smi/binders/saveChangeFormBinder.js';


const ctx = {
    ctxName: 'print_smi',
    tabName: 'form_print_smi',
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

const smi_binders = [SubmitFormBinder];
ctx.registerBinders('form_print_smi', smi_binders);

const list_protocols_binders = [SaveChangeFormBinder, SetActionBinder];
ctx.registerBinders('report_print_smi', list_protocols_binders);


// РЕГИСТРАЦИЯ 
ContextRegistry.register(ctx.ctxName, ctx);
