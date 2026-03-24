export function populateDistricts(targetZone, regionCode, selectedDistrict = null) {
    const raw = targetZone.dataset.districts || "{}";
    const districts = JSON.parse(raw);

    const districtSelect = targetZone.querySelector("#district-select");

    if (!districts || !districtSelect || !regionCode) return;

    districtSelect.innerHTML = '<option value="" disabled>Выберите район</option>';
    districtSelect.disabled = true;

    const prefix = regionCode.substring(0, 2);

    Object.entries(districts).forEach(([code, name]) => {
        code = String(code).padStart(4, "0");

        if (code.startsWith(prefix) && !code.endsWith("00")) {
            const opt = document.createElement("option");
            opt.value = code;
            opt.textContent = name;

            if (selectedDistrict && code === selectedDistrict) {
                opt.selected = true;
            }

            districtSelect.appendChild(opt);
        }
    });

    districtSelect.disabled = false;
    districtSelect.classList.remove("hidden");
}

export function bindRegionDistrict(targetZone) {
    const regionSelect = targetZone.querySelector("#region-select");
    const districtSelect = targetZone.querySelector("#district-select");
    const selectedDistrict = targetZone.dataset.district;

    if (!regionSelect || !districtSelect) return;

    // console.log('*** bindRegionDistrict. regionSelect: ', regionSelect, 'selectedDistrict: ', selectedDistrict);
    // При изменении региона — загружаем районы без selectedDistrict
    regionSelect.addEventListener("change", () => {
        populateDistricts(targetZone, regionSelect.value, null);
    });

    // При загрузке страницы — восстанавливаем выбранный район
    if (regionSelect.value) {
        populateDistricts(targetZone, regionSelect.value, selectedDistrict);
    }

    // Убираем placeholder после выбора
    districtSelect.addEventListener("change", () => {
        const placeholder = districtSelect.querySelector('option[value=""]');
        if (placeholder) placeholder.remove();
    });
}


export function bindPhotoReport(targetZone) {
    //console.log('*** bindPhotoReport. targetZone: ', targetZone);
    const input = targetZone.querySelector("#path_photo");
    const output = targetZone.querySelector("#photo-file-names");

    if (!input || !output) return;

    // 1. ВОССТАНОВЛЕНИЕ УЖЕ ЗАГРУЖЕННЫХ ФОТО
    const raw = targetZone.dataset.pathPhoto;
    if (raw) {
        try {
            const photos = JSON.parse(raw);
            if (Array.isArray(photos) && photos.length > 0) {
                const list = document.createElement("ul");
                list.className = "file-list";

                photos.forEach(photo => {
                    const item = document.createElement("li");
                    item.innerHTML = `<a href="/${photo}" target="_blank">📷 ${photo}</a>`;
                    list.appendChild(item);
                });

                output.appendChild(list);
            }
        } catch (e) {
            console.warn("Failed to parse path_photo:", e);
        }
    }

    // 2. ОБРАБОТКА НОВЫХ ФАЙЛОВ
    input.addEventListener("change", () => {
        output.innerHTML = "";

        if (!input.files.length) return;

        const list = document.createElement("ul");
        list.className = "file-list";

        Array.from(input.files).forEach(file => {
            const item = document.createElement("li");
            item.textContent = file.name;
            list.appendChild(item);
        });

        output.appendChild(list);
    });
}


export function bindBinOrganization(targetZone) {
    const binInput = targetZone.querySelector("#bin-organization");
    const nameInput = targetZone.querySelector("#name-organization");

    if (!binInput || !nameInput) return;

    let lastBin = "";

    binInput.addEventListener("input", () => {
        const bin = binInput.value;

        if (bin.length !== 12) {
            nameInput.value = "";
            lastBin = "";
            return;
        }

        console.log('Bind Bin Organization. BIN: ', bin);
        if (bin === lastBin) return;
        lastBin = bin;

        fetch("/api/organization", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ bin })
        })
            .then(r => r.ok ? r.json() : null)
            .then(data => {
                nameInput.value = data?.name || "";
            })
            .catch(() => {
                nameInput.value = "";
            });
    });
}
