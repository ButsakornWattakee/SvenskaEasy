(function () {
    const fileInput = document.getElementById("imageFile");
    const canvas = document.getElementById("cropCanvas");
    if (!fileInput || !canvas) return;
    const ctx = canvas.getContext("2d");
    const zoomEl = document.getElementById("zoomRange");
    const oxEl = document.getElementById("offsetXRange");
    const oyEl = document.getElementById("offsetYRange");
    let image = null;

    function draw() {
        const zoom = parseFloat(zoomEl.value);
        const ox = parseFloat(oxEl.value);
        const oy = parseFloat(oyEl.value);
        const zoomLabel = document.getElementById("zoomLabel");
        const oxLabel = document.getElementById("oxLabel");
        const oyLabel = document.getElementById("oyLabel");
        if (zoomLabel) zoomLabel.textContent = zoom.toFixed(1);
        if (oxLabel) oxLabel.textContent = ox.toFixed(2);
        if (oyLabel) oyLabel.textContent = oy.toFixed(2);
        ctx.fillStyle = "#002B5C";
        ctx.fillRect(0, 0, 300, 300);
        if (!image) return;
        const w = image.width;
        const h = image.height;
        const minDim = Math.min(w, h);
        let crop = Math.floor(minDim / zoom);
        crop = Math.min(crop, w, h);
        crop = Math.max(crop, 10);
        let cx = w / 2 + ox * 2 * ((w - crop) / 2);
        let cy = h / 2 + oy * 2 * ((h - crop) / 2);
        let left = Math.max(0, Math.floor(cx - crop / 2));
        let top = Math.max(0, Math.floor(cy - crop / 2));
        const box = Math.min(Math.min(w, left + crop) - left, Math.min(h, top + crop) - top);
        ctx.drawImage(image, left, top, box, box, 0, 0, 300, 300);
    }

    fileInput.addEventListener("change", () => {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
            image = new Image();
            image.onload = draw;
            image.src = reader.result;
        };
        reader.readAsDataURL(file);
    });
    [zoomEl, oxEl, oyEl].forEach((el) => el && el.addEventListener("input", draw));
    draw();
})();
