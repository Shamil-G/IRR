export const SetActionBinder = {
    role: 'set-action',

    attachAll(zone = document) {
        if (zone.__roleSetActionBound) return;
        zone.__roleSetActionBound = true;

        zone.addEventListener('click', (e) => {
            const btn = e.target.closest(`[data-role="${this.role}"]`);
            console.log('SetActionBinder. addEventListener click. ZONE: ', zone, '\nBTN: ', btn);
            if (!btn) return;

            e.preventDefault();

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
                const smi = btn.dataset.smi;
                const participants = btn.dataset.participants;
                const event_place = btn.dataset.eventPlace;
                const refer = btn.dataset.refer;

                params.set('event_date', event_date);
                params.set('rfbn_id', rfbn_id);
                params.set('name', name);
                params.set('smi', smi);
                params.set('participants', participants);
                params.set('event_place', event_place);
                params.set('refer', refer);
            }

            console.log('SetActionBinder. params: ', params);

            // Переход на страницу
            window.location.href = `/open_door/action?${params.toString()}`;
        });
    }
};
