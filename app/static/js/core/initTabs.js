import {TabSwitchBinder} from '/static/js/core/tabSwitchBinder.js';


export function initTabs() {
    const tabBinders = [TabSwitchBinder];

    const zone = document.getElementById('tab-panel');
    const zoneName = zone.dataset.zoneName;
    console.log('initTabs. Start on zones: ', zone, ', zoneName; ', zoneName);
    tabBinders.forEach(binder => {
        console.log('initTabs. binder:', binder);
        binder.attachAll(zone, zoneName);
    });
};