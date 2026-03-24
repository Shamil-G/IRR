import { SaveChangeFormBinder } from '/static/js/pages/round_table/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/round_table/binders/setActionBinder.js';
import { setTheme } from '/static/js/functions/setTheme.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
    setTheme();
    console.log('PROTOCOL JS started');
});