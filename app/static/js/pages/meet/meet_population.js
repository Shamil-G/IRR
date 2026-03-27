import * as meet from '/static/js/functions/meet.js'

export function init_meet_population(targetZone){
    meet.bindRegionDistrict(targetZone);
    meet.bindPhotoReport(targetZone);
};

document.addEventListener('DOMContentLoaded', () => {
    const zone = document.getElementById('form_meet_population');
    init_meet_population(zone);
});