export const SetActionBinder = {
    role: 'set-action',

    attachAll(zone = document) {
        if (zone.__roleSetActionBound) return;
        zone.__roleSetActionBound = true;

        console.log('SetActionBinder. ATTACH ALL');

        zone.addEventListener('click', (e) => {
            const btn = e.target.closest(`[data-role="${this.role}"]`);
            console.log('SetActionBinder. addEventListener click. ZONE: ', zone, '\nBTN: ', btn);
            if (!btn) return;

            e.preventDefault();
            e.stopPropagation();

            const action = btn.dataset.action;
            const prot_num = btn.dataset.prot;

            // Собираем параметры
            const params = new URLSearchParams();
            params.set('action', action);
            params.set('prot_num', prot_num);

            if (action == 'edit') {
                const event_date = btn.dataset.eventDate;
                const rfbn_id = btn.dataset.rfbnId;
                const name = btn.dataset.name;
                const channel_name = btn.dataset.channelName;
                const speaker = btn.dataset.speaker;
                const description = btn.dataset.description;

                params.set('event_date', event_date);
                params.set('rfbn_id', rfbn_id);
                params.set('name', name);
                params.set('channel_name', channel_name);
                params.set('speaker', speaker);
                params.set('description', description);
            }

            console.log('SetActionBinder. params: ', params);

            if (action === 'edit') {
                console.log('SetActionBinder. EDIT. ACTION: ', action, ', params: ', params);
                window.location.href = `/radio/action?${params.toString()}`;
            } else {
                console.log('SetActionBinder. POST. ACTION: ', action, ', params: ', params);
                fetch('/radio/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: params.toString()
                }).then(() => {
                    window.location.href = '/radio/protocol';
                });
            }
        });
    }
};
