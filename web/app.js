class FaceReplacer {
    constructor() {
        this.canvas = document.getElementById('mainCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.placeholder = document.getElementById('placeholder');
        this.previewContainer = document.getElementById('previewContainer');
        this.selectedInfo = document.getElementById('selectedInfo');

        this.mainImage = null;
        this.elements = {};
        this.selectedElement = null;
        this.dragging = false;
        this.dragStart = null;
        this.resizeHandle = null;

        this.presets = {
            eyeLeft: null,
            eyeRight: null,
            mouth: null
        };

        this.isProcessed = false;
        this.initEventListeners();
    }

    initEventListeners() {
        document.getElementById('imageInput').addEventListener('change', (e) => this.handleImageUpload(e));
        document.getElementById('eyeLeftInput').addEventListener('change', (e) => this.handlePresetUpload(e, 'eyeLeft'));
        document.getElementById('eyeRightInput').addEventListener('change', (e) => this.handlePresetUpload(e, 'eyeRight'));
        document.getElementById('mouthInput').addEventListener('change', (e) => this.handlePresetUpload(e, 'mouth'));
        document.getElementById('processBtn').addEventListener('click', () => this.startProcessing());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetElements());
        document.getElementById('saveBtn').addEventListener('click', () => this.saveResult());

        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.handleMouseUp());
        this.canvas.addEventListener('mouseleave', () => this.handleMouseUp());

        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }

    handleImageUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                this.mainImage = img;
                this.canvas.width = img.width;
                this.canvas.height = img.height;
                this.canvas.style.display = 'block';
                this.placeholder.style.display = 'none';
                document.getElementById('processBtn').disabled = false;
                this.drawImage();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    handlePresetUpload(e, type) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                this.presets[type] = img;
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    startProcessing() {
        if (!this.mainImage) return;

        this.resetElements();
        this.isProcessed = true;
        document.getElementById('resetBtn').disabled = false;
        document.getElementById('saveBtn').disabled = false;
        this.draw();
    }

    resetElements() {
        if (!this.mainImage) return;

        const imgWidth = this.mainImage.width;
        const imgHeight = this.mainImage.height;

        this.elements = {
            eyeLeft: {
                name: 'eyeLeft',
                displayName: '左眼',
                x: imgWidth / 4,
                y: imgHeight / 3,
                width: 100,
                height: 60,
                color: '#ff0000'
            },
            eyeRight: {
                name: 'eyeRight',
                displayName: '右眼',
                x: (imgWidth * 3) / 4,
                y: imgHeight / 3,
                width: 100,
                height: 60,
                color: '#00ff00'
            },
            mouth: {
                name: 'mouth',
                displayName: '嘴巴',
                x: imgWidth / 2,
                y: (imgHeight * 2) / 3,
                width: 120,
                height: 40,
                color: '#0000ff'
            }
        };

        this.selectedElement = null;
        this.updateSelectedInfo();
        this.draw();
    }

    drawImage() {
        if (!this.mainImage) return;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.drawImage(this.mainImage, 0, 0);
    }

    draw() {
        this.drawImage();

        if (!this.isProcessed) return;

        Object.values(this.elements).forEach(elem => {
            this.drawElement(elem);
        });

        if (this.selectedElement) {
            this.drawSelection(this.selectedElement);
        }
    }

    drawElement(elem) {
        const preset = this.presets[elem.name];
        if (preset) {
            this.ctx.drawImage(preset, elem.x - elem.width / 2, elem.y - elem.height / 2, elem.width, elem.height);
        } else {
            this.ctx.strokeStyle = elem.color;
            this.ctx.lineWidth = 1;
            this.ctx.setLineDash([5, 5]);
            this.ctx.strokeRect(elem.x - elem.width / 2, elem.y - elem.height / 2, elem.width, elem.height);
            this.ctx.setLineDash([]);
        }
    }

    drawSelection(elem) {
        this.ctx.strokeStyle = '#ff0000';
        this.ctx.lineWidth = 1;
        this.ctx.setLineDash([5, 5]);
        this.ctx.strokeRect(elem.x - elem.width / 2, elem.y - elem.height / 2, elem.width, elem.height);
        this.ctx.setLineDash([]);

        const handles = this.getHandles(elem);
        this.ctx.fillStyle = '#ffffff';
        this.ctx.strokeStyle = '#ff0000';
        this.ctx.lineWidth = 1;

        Object.values(handles).forEach(handle => {
            this.ctx.beginPath();
            this.ctx.arc(handle.x, handle.y, 5, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.stroke();
        });
    }

    getHandles(elem) {
        const halfW = elem.width / 2;
        const halfH = elem.height / 2;

        return {
            topLeft: { x: elem.x - halfW, y: elem.y - halfH },
            topRight: { x: elem.x + halfW, y: elem.y - halfH },
            bottomLeft: { x: elem.x - halfW, y: elem.y + halfH },
            bottomRight: { x: elem.x + halfW, y: elem.y + halfH },
            top: { x: elem.x, y: elem.y - halfH },
            bottom: { x: elem.x, y: elem.y + halfH },
            left: { x: elem.x - halfW, y: elem.y },
            right: { x: elem.x + halfW, y: elem.y }
        };
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }

    handleMouseDown(e) {
        if (!this.isProcessed) return;

        const pos = this.getMousePos(e);

        const handle = this.getClickedHandle(pos);
        if (handle) {
            this.resizeHandle = handle;
            this.dragStart = pos;
            return;
        }

        const elem = this.getClickedElement(pos);
        if (elem) {
            this.selectedElement = elem;
            this.dragging = true;
            this.dragStart = pos;
            this.updateSelectedInfo();
            this.draw();
            return;
        }

        this.selectedElement = null;
        this.updateSelectedInfo();
        this.draw();
    }

    handleMouseMove(e) {
        if (!this.isProcessed) return;

        const pos = this.getMousePos(e);

        if (this.resizeHandle) {
            this.handleResize(pos);
            this.draw();
            return;
        }

        if (this.dragging && this.selectedElement) {
            const dx = pos.x - this.dragStart.x;
            const dy = pos.y - this.dragStart.y;
            this.selectedElement.x += dx;
            this.selectedElement.y += dy;
            this.dragStart = pos;
            this.draw();
            return;
        }

        const handle = this.getClickedHandle(pos);
        const elem = this.getClickedElement(pos);
        this.canvas.style.cursor = handle ? 'pointer' : (elem ? 'move' : 'default');
    }

    handleMouseUp() {
        this.dragging = false;
        this.resizeHandle = null;
        this.dragStart = null;
    }

    getClickedHandle(pos) {
        if (!this.selectedElement) return null;

        const handles = this.getHandles(this.selectedElement);
        const threshold = 10;

        for (const [name, handle] of Object.entries(handles)) {
            const dist = Math.sqrt(Math.pow(pos.x - handle.x, 2) + Math.pow(pos.y - handle.y, 2));
            if (dist <= threshold) {
                return { name, ...handle };
            }
        }

        return null;
    }

    getClickedElement(pos) {
        for (const elem of Object.values(this.elements)) {
            const halfW = elem.width / 2;
            const halfH = elem.height / 2;

            if (pos.x >= elem.x - halfW && pos.x <= elem.x + halfW &&
                pos.y >= elem.y - halfH && pos.y <= elem.y + halfH) {
                return elem;
            }
        }
        return null;
    }

    handleResize(pos) {
        if (!this.resizeHandle || !this.selectedElement) return;

        const elem = this.selectedElement;
        const dx = pos.x - this.dragStart.x;
        const dy = pos.y - this.dragStart.y;

        switch (this.resizeHandle.name) {
            case 'topLeft':
                elem.x += dx;
                elem.y += dy;
                elem.width -= dx;
                elem.height -= dy;
                break;
            case 'topRight':
                elem.y += dy;
                elem.width += dx;
                elem.height -= dy;
                break;
            case 'bottomLeft':
                elem.x += dx;
                elem.width -= dx;
                elem.height += dy;
                break;
            case 'bottomRight':
                elem.width += dx;
                elem.height += dy;
                break;
            case 'top':
                elem.y += dy;
                elem.height -= dy;
                break;
            case 'bottom':
                elem.height += dy;
                break;
            case 'left':
                elem.x += dx;
                elem.width -= dx;
                break;
            case 'right':
                elem.width += dx;
                break;
        }

        elem.width = Math.max(10, elem.width);
        elem.height = Math.max(10, elem.height);
        this.dragStart = pos;
    }

    updateSelectedInfo() {
        if (!this.selectedElement) {
            this.selectedInfo.innerHTML = '<p>未选中任何元素</p>';
            return;
        }

        const elem = this.selectedElement;
        this.selectedInfo.innerHTML = `
            <p><strong>${elem.displayName}</strong></p>
            <p>位置: (${Math.round(elem.x)}, ${Math.round(elem.y)})</p>
            <p>大小: ${Math.round(elem.width)} × ${Math.round(elem.height)}</p>
        `;
    }

    handleKeyDown(e) {
        if (!this.isProcessed) return;

        if (e.key === 's' || e.key === 'S') {
            e.preventDefault();
            this.saveResult();
        } else if (e.key === 'r' || e.key === 'R') {
            e.preventDefault();
            this.resetElements();
        } else if (e.key === 'Escape') {
            this.selectedElement = null;
            this.updateSelectedInfo();
            this.draw();
        }
    }

    saveResult() {
        if (!this.isProcessed) return;

        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        const tempCtx = tempCanvas.getContext('2d');

        tempCtx.drawImage(this.mainImage, 0, 0);

        Object.values(this.elements).forEach(elem => {
            const preset = this.presets[elem.name];
            if (preset) {
                tempCtx.drawImage(preset, elem.x - elem.width / 2, elem.y - elem.height / 2, elem.width, elem.height);
            }
        });

        const dataURL = tempCanvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = 'output.png';
        link.href = dataURL;
        link.click();

        this.previewContainer.innerHTML = `<img src="${dataURL}" alt="Result">`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new FaceReplacer();
});