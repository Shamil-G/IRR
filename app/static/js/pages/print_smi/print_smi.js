import { SaveChangeFormBinder } from '/static/js/pages/print_smi/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/print_smi/binders/setActionBinder.js';

document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
    console.log('PROTOCOL JS started');
});