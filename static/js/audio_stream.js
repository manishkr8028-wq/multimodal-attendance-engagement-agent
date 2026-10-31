/**
 * Audio Stream & Real-time Acoustic Waveform Visualizer
 * Analyzes microphone energy using Web Audio API.
 */

class AudioStreamController {
  constructor() {
    this.audioCtx = null;
    this.analyser = null;
    this.micStream = null;
    this.dataArray = null;
    this.isListening = false;
    this.simulatedPhase = 0;

    this.currentRMS = 0.02;
    this.currentPeak = 0.04;

    this.bars = document.querySelectorAll('.audio-bar');
  }

  async startAudio() {
    try {
      this.micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContext();
      const source = this.audioCtx.createMediaStreamSource(this.micStream);

      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 64;
      source.connect(this.analyser);

      const bufferLength = this.analyser.frequencyBinCount;
      this.dataArray = new Uint8Array(bufferLength);
      this.isListening = true;

      this.startVisualizerLoop();
      return true;
    } catch (err) {
      console.warn("Microphone access unavailable or denied. Operating in Simulated Audio Telemetry mode:", err);
      this.isListening = false;
      this.startSimulatedAudioLoop();
      return false;
    }
  }

  stopAudio() {
    if (this.micStream) {
      this.micStream.getTracks().forEach(t => t.stop());
      this.micStream = null;
    }
    if (this.audioCtx) {
      this.audioCtx.close();
      this.audioCtx = null;
    }
    this.isListening = false;
  }

  startVisualizerLoop() {
    const loop = () => {
      if (!this.isListening || !this.analyser) return;
      this.analyser.getByteFrequencyData(this.dataArray);

      // Compute RMS
      let sum = 0;
      let peak = 0;
      for (let i = 0; i < this.dataArray.length; i++) {
        const val = this.dataArray[i] / 255.0;
        sum += val * val;
        if (val > peak) peak = val;
      }
      this.currentRMS = Math.sqrt(sum / this.dataArray.length);
      this.currentPeak = peak;

      this.renderBars(this.dataArray);
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  startSimulatedAudioLoop() {
    const simLoop = () => {
      this.simulatedPhase += 0.08;
      const baseEnergy = 0.035 + Math.sin(this.simulatedPhase * 0.7) * 0.025;
      const randomNoise = (Math.random() - 0.5) * 0.015;
      this.currentRMS = Math.max(0.005, baseEnergy + randomNoise);
      this.currentPeak = this.currentRMS * 1.8;

      // Update bars with simulated dynamic heights
      if (this.bars && this.bars.length > 0) {
        this.bars.forEach((bar, idx) => {
          const wave = Math.sin(this.simulatedPhase * 1.2 + idx * 0.4);
          const height = Math.max(4, Math.round(18 + wave * 16 + Math.random() * 8));
          bar.style.height = `${height}px`;
        });
      }
      requestAnimationFrame(simLoop);
    };
    requestAnimationFrame(simLoop);
  }

  renderBars(freqData) {
    if (!this.bars || this.bars.length === 0) return;
    const len = Math.min(this.bars.length, freqData.length);
    for (let i = 0; i < len; i++) {
      const val = freqData[i] || 0;
      const height = Math.max(4, Math.round((val / 255.0) * 44));
      this.bars[i].style.height = `${height}px`;
    }
  }

  getLiveMetrics() {
    return {
      rms: Math.round(this.currentRMS * 1000) / 1000,
      peak: Math.round(this.currentPeak * 1000) / 1000
    };
  }
}

window.audioController = new AudioStreamController();
