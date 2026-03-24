import * as meet from '/static/js/functions/meet.js'
import { setTheme } from '/static/js/functions/setTheme.js'

export function init_meet_population(targetZone){
    meet.bindRegionDistrict(targetZone);
    meet.bindPhotoReport(targetZone);
    setTheme();
};

document.addEventListener('DOMContentLoaded', () => {
    const zone = document.getElementById('form_meet_population');
    init_meet_population(zone);
});