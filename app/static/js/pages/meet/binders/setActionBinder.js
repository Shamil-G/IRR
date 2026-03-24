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
            const page = btn.dataset.page;

            // Собираем параметры
            const params = new URLSearchParams();
            params.set('action', action);
            params.set('prot_num', prot_num);

            if (action == 'edit' && page) {
                const date_irr = btn.dataset.dateIrr;
                const name = btn.dataset.name;
                const rfbn_id = btn.dataset.rfbnId;
                const district = btn.dataset.district;
                const cnt_total = btn.dataset.cntTotal;
                const cnt_women = btn.dataset.cntWomen;
                const speaker = btn.dataset.speaker;
                const meeting_format = btn.dataset.meetingFormat;
                const meeting_place = btn.dataset.meetingPlace;
                const bin = btn.dataset.bin;
                const category = btn.dataset.category;
                const partners = btn.dataset.partners;
                const path_photo = btn.dataset.pathPhoto;

                params.set('date_irr', date_irr);
                params.set('page', page);
                params.set('name', name);

                params.set('rfbn_id', rfbn_id);
                params.set('district', district);
                params.set('cnt_total', cnt_total);
                params.set('cnt_women', cnt_women);
                params.set('speaker', speaker);
                params.set('meeting_format', meeting_format);
                params.set('meeting_place', meeting_place);
                params.set('category', category);
                params.set('bin', bin);
                params.set('partners', partners);
                params.set('path_photo', path_photo);
            }

            console.log('SetActionBinder. params: ', params);

            // Переход на страницу
            window.location.href = `/meet/action?${params.toString()}`;
        });
    }
};
