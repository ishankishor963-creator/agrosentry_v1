/**
 * camera.js
 * ---------
 * Zero-latency client-side WebRTC camera streaming and frame grabber.
 * Interacts directly with HTML5 MediaDevices API without full-page reloads.
 */

class FarmCamera {
  constructor(videoElementId, canvasElementId) {
    this.video = document.getElementById(videoElementId);
    this.canvas = document.getElementById(canvasElementId) || document.createElement('canvas');
    this.stream = null;
    this.facingMode = 'environment'; // default to rear camera on mobile
    this.isStreaming = false;
  }

  async startStream() {
    this.stopStream(); // clean up any existing stream

    const constraints = {
      video: {
        facingMode: { ideal: this.facingMode },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    };

    try {
      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;
      await this.video.play();
      this.isStreaming = true;
      return true;
    } catch (err) {
      console.warn("Primary camera constraint failed, falling back to basic video:", err);
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        this.video.srcObject = this.stream;
        await this.video.play();
        this.isStreaming = true;
        return true;
      } catch (fallbackErr) {
        console.error("Camera access denied or unavailable:", fallbackErr);
        this.isStreaming = false;
        return false;
      }
    }
  }

  stopStream() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
      this.video.srcObject = null;
      this.isStreaming = false;
    }
  }

  toggleFacingMode() {
    this.facingMode = this.facingMode === 'environment' ? 'user' : 'environment';
    return this.startStream();
  }

  /**
   * Captures the current video frame directly into an optimized JPEG base64 string.
   * Scales to 640px max dimension for fast transmission and instant 224x224 server prep.
   */
  captureFrame() {
    if (!this.isStreaming || !this.video.videoWidth) {
      return null;
    }

    const vw = this.video.videoWidth;
    const vh = this.video.videoHeight;

    // Crop center square to match reticle target
    const size = Math.min(vw, vh);
    const sx = (vw - size) / 2;
    const sy = (vh - size) / 2;

    this.canvas.width = 448; // crisp 2x resolution for model's 224x224 input
    this.canvas.height = 448;

    const ctx = this.canvas.getContext('2d');
    ctx.drawImage(this.video, sx, sy, size, size, 0, 0, 448, 448);

    return this.canvas.toDataURL('image/jpeg', 0.88);
  }
}

window.FarmCamera = FarmCamera;
