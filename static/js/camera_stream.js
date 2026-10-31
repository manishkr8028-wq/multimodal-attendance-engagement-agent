/**
 * Camera Stream & Real-time Canvas HUD Controller
 * Handles webcam capture, frame rendering, and drawing AI bounding box overlays.
 */

class CameraHUDController {
  constructor() {
    this.video = document.getElementById('camera-video');
    this.canvas = document.getElementById('hud-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.stream = null;
    this.isStreaming = false;
    this.isSimulationMode = false;

    this.latestDetections = [];
    this.simulatedTime = 0;

    this.initEventListeners();
  }

  initEventListeners() {
    const simBtn = document.getElementById('toggle-sim-btn');
    if (simBtn) {
      simBtn.addEventListener('click', () => this.toggleSimulationMode());
    }

    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    if (!this.canvas || !this.video) return;
    this.canvas.width = this.video.clientWidth || 640;
    this.canvas.height = this.video.clientHeight || 360;
  }

  async startCamera() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      this.video.srcObject = this.stream;
      await this.video.play();
      this.isStreaming = true;
      this.isSimulationMode = false;
      this.resizeCanvas();
      this.startHUDAnimation();
      return true;
    } catch (err) {
      console.warn("Webcam access unavailable or denied. Enabling Classroom Simulation Mode:", err);
      this.enableSimulationMode();
      return false;
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    this.isStreaming = false;
  }

  toggleSimulationMode() {
    if (this.isSimulationMode) {
      this.startCamera();
    } else {
      this.enableSimulationMode();
    }
  }

  enableSimulationMode() {
    this.stopCamera();
    this.isSimulationMode = true;
    this.isStreaming = true;
    this.resizeCanvas();
    this.startHUDAnimation();

    const simBtn = document.getElementById('toggle-sim-btn');
    if (simBtn) {
      simBtn.innerHTML = '<i data-lucide="camera" style="width:14px; height:14px;"></i> Switch to Live Camera';
      if (window.lucide) lucide.createIcons();
    }
  }

  captureFrameBase64() {
    if (this.isSimulationMode || !this.video || !this.isStreaming) {
      return null;
    }

    try {
      const offscreen = document.createElement('canvas');
      offscreen.width = 480;
      offscreen.height = 270;
      const offCtx = offscreen.getContext('2d');
      offCtx.drawImage(this.video, 0, 0, offscreen.width, offscreen.height);
      return offscreen.toDataURL('image/jpeg', 0.65);
    } catch (e) {
      return null;
    }
  }

  updateDetections(visionData) {
    if (visionData && visionData.faces) {
      this.latestDetections = visionData.faces;
    }
  }

  startHUDAnimation() {
    const renderLoop = () => {
      this.renderHUD();
      requestAnimationFrame(renderLoop);
    };
    requestAnimationFrame(renderLoop);
  }

  renderHUD() {
    if (!this.ctx || !this.canvas) return;
    const w = this.canvas.width;
    const h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);

    if (this.isSimulationMode) {
      this.renderSimulationBackground(w, h);
    }

    // Draw active face bounding boxes and HUD tags
    const facesToRender = this.isSimulationMode ? this.getSimulatedFaces(w, h) : this.latestDetections;

    facesToRender.forEach((face, idx) => {
      this.drawFaceBox(face, w, h, idx);
    });
  }

  renderSimulationBackground(w, h) {
    this.simulatedTime += 0.03;
    const ctx = this.ctx;

    // Draw dark classroom simulation backdrop
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, '#090d16');
    grad.addColorStop(1, '#05070d');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Grid matrix lines
    ctx.strokeStyle = 'rgba(99, 102, 241, 0.08)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Simulation watermark
    ctx.fillStyle = 'rgba(148, 163, 184, 0.4)';
    ctx.font = '12px Outfit, sans-serif';
    ctx.fillText('CLASSROOM BENCHMARK SIMULATION ACTIVE (SYNTHETIC TELEMETRY)', 20, h - 20);
  }

  getSimulatedFaces(w, h) {
    const t = this.simulatedTime;
    const jitterX = Math.sin(t * 1.5) * 8;
    const jitterY = Math.cos(t * 1.2) * 5;

    return [
      {
        track_id: 1,
        bbox: {
          x: Math.round(w * 0.35 + jitterX),
          y: Math.round(h * 0.28 + jitterY),
          w: Math.round(w * 0.28),
          h: Math.round(h * 0.48)
        },
        sustained_seconds: 14.5 + Math.sin(t) * 2,
        sustained_threshold_met: true,
        attendance_status: 'Present',
        pitch: Math.round(Math.sin(t) * 4 * 10) / 10,
        yaw: Math.round(Math.cos(t * 0.8) * 6 * 10) / 10,
        attention_score: 0.88 + Math.sin(t) * 0.05
      }
    ];
  }

  drawFaceBox(face, canvasW, canvasH, idx) {
    const ctx = this.ctx;
    let { x, y, w, h } = face.bbox;

    // Coordinate normalization if raw dimensions come from backend 480x270
    if (x < 480 && canvasW > 500 && !this.isSimulationMode) {
      const scaleX = canvasW / 480;
      const scaleY = canvasH / 270;
      x = x * scaleX;
      y = y * scaleY;
      w = w * scaleX;
      h = h * scaleY;
    }

    const isSustained = face.sustained_threshold_met;
    const boxColor = isSustained ? '#10b981' : '#6366f1';

    // 1. Draw glowing corner brackets
    ctx.strokeStyle = boxColor;
    ctx.lineWidth = 2.5;
    const corner = Math.min(22, w * 0.2);

    // Top-left
    ctx.beginPath();
    ctx.moveTo(x, y + corner);
    ctx.lineTo(x, y);
    ctx.lineTo(x + corner, y);
    ctx.stroke();

    // Top-right
    ctx.beginPath();
    ctx.moveTo(x + w - corner, y);
    ctx.lineTo(x + w, y);
    ctx.lineTo(x + w, y + corner);
    ctx.stroke();

    // Bottom-left
    ctx.beginPath();
    ctx.moveTo(x, y + h - corner);
    ctx.lineTo(x, y + h);
    ctx.lineTo(x + corner, y + h);
    ctx.stroke();

    // Bottom-right
    ctx.beginPath();
    ctx.moveTo(x + w - corner, y + h);
    ctx.lineTo(x + w, y + h);
    ctx.lineTo(x + w, y + h - corner);
    ctx.stroke();

    // 2. Draw subtle translucent fill
    ctx.fillStyle = isSustained ? 'rgba(16, 185, 129, 0.05)' : 'rgba(99, 102, 241, 0.05)';
    ctx.fillRect(x, y, w, h);

    // 3. Header badge on top of box
    const label = `Student #${face.track_id || idx + 1} | ${isSustained ? 'VERIFIED PRESENT' : 'VERIFYING...'}`;
    ctx.font = 'bold 11px Outfit, Inter, sans-serif';
    const textWidth = ctx.measureText(label).width;

    ctx.fillStyle = boxColor;
    ctx.fillRect(x, Math.max(0, y - 22), textWidth + 14, 20);

    ctx.fillStyle = '#ffffff';
    ctx.fillText(label, x + 7, Math.max(14, y - 8));

    // 4. Sub-tag below box: Sustained time & Pose angle
    const subLabel = `Presence: ${face.sustained_seconds || 0}s | Gaze: ${Math.round((face.attention_score || 0.8) * 100)}%`;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
    ctx.fillRect(x, y + h + 4, ctx.measureText(subLabel).width + 12, 18);

    ctx.fillStyle = '#a5b4fc';
    ctx.font = '10px Outfit, sans-serif';
    ctx.fillText(subLabel, x + 6, y + h + 17);
  }
}

window.cameraController = new CameraHUDController();
