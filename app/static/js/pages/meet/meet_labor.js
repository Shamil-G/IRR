import * as meet from '/static/js/functions/meet.js'

function init_meet_labor(targetZone){
    meet.bindRegionDistrict(targetZone);
    meet.bindPhotoReport(targetZone);
    meet.bindBinOrganization(targetZone);
}

document.addEventListener('DOMContentLoaded', () => {
    const zone = document.getElementById('form_meet_labor');
    init_meet_labor(zone);
});
