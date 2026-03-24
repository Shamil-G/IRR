import { SaveChangeFormBinder } from '/static/js/pages/meet/binders/saveChangeFormBinder.js';
import { SetActionBinder } from '/static/js/pages/meet/binders/setActionBinder.js';


document.addEventListener('DOMContentLoaded', () => {
    SaveChangeFormBinder.attachAll(document);
    SetActionBinder.attachAll(document);
    console.log('PROTOCOL JS started');
});
