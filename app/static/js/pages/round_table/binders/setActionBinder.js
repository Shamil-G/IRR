export const SetActionBinder = {
    role: 'set-action',

    attachAll(zone = document) {
        if (zone.__roleSetActionBound) return;
        zone.__roleSetActionBound = true;

        zone.addEventListener('click', (e) => {
            const btn = e.target.closest(`[data-role="${this.role}"]`);
            //console.log('SetActionBinder. addEventListener click. ZONE: ', zone, '\nBTN: ', btn);
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
                const participants = btn.dataset.participants;
                const description = btn.dataset.description;
                const refer = btn.dataset.refer;

                params.set('event_date', event_date);
                params.set('rfbn_id', rfbn_id);
                params.set('name', name);
                params.set('participants', participants);
                params.set('description', description);
                params.set('refer', refer);
            }

            //console.log('SetActionBinder. params: ', params);

            // Переход на страницу
            if (action === 'edit') {
                //console.log('SetActionBinder. EDIT. ACTION: ', action, ', params: ', params);
                window.location.href = `/round_table/action?${params.toString()}`;
            } else {
                //console.log('SetActionBinder. ROUND_TABLE. POST. ACTION: ', action, ', params: ', params);
                fetch('/round_table/action', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: params.toString()
                }).then(() => {
                    window.location.href = '/round_table/protocol';
                });
            }

        });
    }
};
