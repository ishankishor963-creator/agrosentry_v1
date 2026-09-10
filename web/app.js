/**
 * app.js
 * ------
 * Client application controller for AgroSentry modern web frontend.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation & Views
  const navBtns = document.querySelectorAll('.nav-btn');
  const sections = document.querySelectorAll('.view-section');
  let currentView = 'dashboard';

  // Camera Instance
  const camera = new window.FarmCamera('cameraVideo', 'snapshotCanvas');

  // Elements: Scanner Sub-Tabs
  const tabCameraBtn = document.getElementById('tabCameraBtn');
  const tabUploadBtn = document.getElementById('tabUploadBtn');
  const cameraMode = document.getElementById('cameraMode');
  const uploadMode = document.getElementById('uploadMode');

  // Elements: Camera Controls
  const snapBtn = document.getElementById('snapBtn');
  const switchCamBtn = document.getElementById('switchCamBtn');
  const retakeBtn = document.getElementById('retakeBtn');

  // Elements: Upload & Preview
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const previewBox = document.getElementById('previewBox');
  const previewImg = document.getElementById('previewImg');
  const analyzeUploadBtn = document.getElementById('analyzeUploadBtn');
  const clearUploadBtn = document.getElementById('clearUploadBtn');

  // Elements: Results
  const resultPlaceholder = document.getElementById('resultPlaceholder');
  const resultContent = document.getElementById('resultContent');
  const resultBadge = document.getElementById('resultBadge');
  const resultTitle = document.getElementById('resultTitle');
  const resultConfidence = document.getElementById('resultConfidence');
  const progressFill = document.getElementById('progressFill');
  const rankingContainer = document.getElementById('rankingContainer');
  const clinicalDescription = document.getElementById('clinicalDescription');
  const agronomicTreatment = document.getElementById('agronomicTreatment');
  const inferenceBadge = document.getElementById('inferenceBadge');

  // Elements: Spinner
  const scannerSpinner = document.getElementById('scannerSpinner');
  const spinnerText = document.getElementById('spinnerText');

  // Elements: Telemetry
  const valMoisture = document.getElementById('valMoisture');
  const valHumidity = document.getElementById('valHumidity');
  const valTemp = document.getElementById('valTemp');
  const valLight = document.getElementById('valLight');
  const badgeMoisture = document.getElementById('badgeMoisture');
  const badgeTemp = document.getElementById('badgeTemp');
  const deviceStatusPill = document.getElementById('deviceStatusPill');
  const deviceDot = document.getElementById('deviceDot');
  const deviceText = document.getElementById('deviceText');

  // Elements: Device Modal
  const deviceModal = document.getElementById('deviceModal');
  const deviceIpInput = document.getElementById('deviceIpInput');
  const saveDeviceBtn = document.getElementById('saveDeviceBtn');
  const closeDeviceBtn = document.getElementById('closeDeviceBtn');

  // Elements: Alerts View
  const droughtCard = document.getElementById('droughtCard');
  const droughtBadge = document.getElementById('droughtBadge');
  const droughtDesc = document.getElementById('droughtDesc');
  const floodCard = document.getElementById('floodCard');
  const floodBadge = document.getElementById('floodBadge');
  const floodDesc = document.getElementById('floodDesc');

  // Elements: Chat
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendChatBtn = document.getElementById('sendChatBtn');
  const chatChips = document.querySelectorAll('.chat-chip');

  let selectedFileBase64 = null;

  // ----------------- Navigation -----------------
  function switchView(targetView) {
    currentView = targetView;
    navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === targetView);
    });
    sections.forEach(sec => {
      sec.classList.toggle('active', sec.id === `view-${targetView}`);
    });

    // Camera Lifecycle: only stream when on scanner tab with camera mode active
    if (targetView === 'scanner' && cameraMode.style.display !== 'none') {
      camera.startStream();
    } else {
      camera.stopStream();
    }

    if (targetView === 'alerts') {
      fetchAlerts();
    }
  }

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
  });

  // ----------------- Scanner Sub-tabs -----------------
  tabCameraBtn.addEventListener('click', () => {
    tabCameraBtn.classList.add('active');
    tabUploadBtn.classList.remove('active');
    cameraMode.style.display = 'block';
    uploadMode.style.display = 'none';
    camera.startStream();
  });

  tabUploadBtn.addEventListener('click', () => {
    tabUploadBtn.classList.add('active');
    tabCameraBtn.classList.remove('active');
    uploadMode.style.display = 'block';
    cameraMode.style.display = 'none';
    camera.stopStream();
  });

  // ----------------- Camera Actions -----------------
  snapBtn.addEventListener('click', async () => {
    const frameData = camera.captureFrame();
    if (!frameData) {
      alert('Camera stream is not ready. Please verify camera permissions.');
      return;
    }
    await runInference(frameData);
  });

  switchCamBtn.addEventListener('click', async () => {
    await camera.toggleFacingMode();
  });

  // ----------------- File Drag & Drop -----------------
  dropZone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleImageFile(file);
    }
  });

  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      handleImageFile(file);
    }
  });

  function handleImageFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedFileBase64 = e.target.result;
      previewImg.src = selectedFileBase64;
      dropZone.style.display = 'none';
      previewBox.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  clearUploadBtn.addEventListener('click', () => {
    selectedFileBase64 = null;
    fileInput.value = '';
    previewImg.src = '';
    dropZone.style.display = 'block';
    previewBox.style.display = 'none';
  });

  analyzeUploadBtn.addEventListener('click', async () => {
    if (!selectedFileBase64) {
      alert('Please select or drop an image file first.');
      return;
    }
    await runInference(selectedFileBase64);
  });

  // ----------------- Inference API -----------------
  async function runInference(imageBase64) {
    showSpinner('Running MobileNetV2 Neural Network Inference...');
    try {
      const resp = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: imageBase64 })
      });

      const data = await resp.json();
      if (!data.success) {
        throw new Error(data.error || 'Diagnosis failed');
      }

      renderDiagnosis(data.prediction);
    } catch (err) {
      console.error(err);
      alert('Error during leaf diagnosis: ' + err.message);
    } finally {
      hideSpinner();
    }
  }

  function renderDiagnosis(pred) {
    resultPlaceholder.style.display = 'none';
    resultContent.style.display = 'block';

    // Status Badge
    if (pred.is_healthy) {
      resultBadge.className = 'result-badge badge-optimal';
      resultBadge.innerHTML = '<span>✅</span> Healthy Plant Foliage';
      progressFill.className = 'progress-fill healthy';
    } else {
      resultBadge.className = 'result-badge badge-danger';
      resultBadge.innerHTML = '<span>⚠️</span> Pathogen Infection Detected';
      progressFill.className = 'progress-fill disease';
    }

    resultTitle.textContent = pred.display_name;
    resultConfidence.textContent = `${pred.confidence}%`;
    progressFill.style.width = `${Math.min(pred.confidence, 100)}%`;

    if (pred.inference_time_ms) {
      inferenceBadge.textContent = `⚡ Inference: ${pred.inference_time_ms} ms (MobileNetV2)`;
    }

    // Top 3 rankings
    rankingContainer.innerHTML = '';
    if (pred.rankings && pred.rankings.length) {
      pred.rankings.forEach(item => {
        const row = document.createElement('div');
        row.className = 'ranking-item';
        row.innerHTML = `
          <span>${item.display_name}</span>
          <strong style="font-family:'Space Grotesk'">${item.confidence}%</strong>
        `;
        rankingContainer.appendChild(row);
      });
    }

    clinicalDescription.textContent = pred.description;
    agronomicTreatment.textContent = pred.treatment;

    // Smooth scroll into results on mobile
    if (window.innerWidth < 900) {
      resultContent.scrollIntoView({ behavior: 'smooth' });
    }
  }

  function showSpinner(text) {
    spinnerText.textContent = text || 'Processing...';
    scannerSpinner.style.display = 'flex';
  }

  function hideSpinner() {
    scannerSpinner.style.display = 'none';
  }

  // ----------------- Live Sensors Polling -----------------
  async function fetchTelemetry() {
    try {
      const resp = await fetch('/api/sensors');
      const data = await resp.json();

      valMoisture.textContent = data.soil_moisture;
      valHumidity.textContent = data.humidity;
      valTemp.textContent = data.temperature;
      valLight.textContent = data.light_lux;

      // Status badges
      if (data.soil_status === 'optimal') {
        badgeMoisture.className = 'metric-badge badge-optimal';
        badgeMoisture.textContent = '● Optimal Moisture';
      } else if (data.soil_status === 'low') {
        badgeMoisture.className = 'metric-badge badge-warning';
        badgeMoisture.textContent = '▲ Water Depleted';
      } else {
        badgeMoisture.className = 'metric-badge badge-danger';
        badgeMoisture.textContent = '▼ Water Saturated';
      }

      if (data.temp_status === 'optimal') {
        badgeTemp.className = 'metric-badge badge-optimal';
        badgeTemp.textContent = '● Ideal Range';
      } else {
        badgeTemp.className = 'metric-badge badge-warning';
        badgeTemp.textContent = '▲ Thermal Stress';
      }

      if (data.source === 'device') {
        deviceDot.className = 'status-dot';
        deviceText.textContent = 'Hardware Online (ESP32)';
      } else {
        deviceDot.className = 'status-dot amber';
        deviceText.textContent = 'Demo Mode (Simulated)';
      }
    } catch (e) {
      console.warn('Telemetry fetch error:', e);
    }
  }

  setInterval(fetchTelemetry, 3500);
  fetchTelemetry();

  // ----------------- Alerts View -----------------
  async function fetchAlerts() {
    try {
      const resp = await fetch('/api/alerts');
      const data = await resp.json();

      // Drought
      droughtBadge.textContent = data.drought.level;
      droughtBadge.className = `metric-badge badge-${data.drought.level.toLowerCase() === 'normal' ? 'optimal' : (data.drought.level.toLowerCase() === 'critical' ? 'danger' : 'warning')}`;
      droughtDesc.textContent = data.drought.description;

      // Flood
      floodBadge.textContent = data.flood.level;
      floodBadge.className = `metric-badge badge-${data.flood.level.toLowerCase() === 'normal' ? 'optimal' : 'danger'}`;
      floodDesc.textContent = data.flood.description;
    } catch (e) {
      console.warn('Alerts fetch error:', e);
    }
  }

  // ----------------- Hardware Modal -----------------
  deviceStatusPill.addEventListener('click', () => {
    deviceModal.classList.add('active');
  });

  closeDeviceBtn.addEventListener('click', () => {
    deviceModal.classList.remove('active');
  });

  saveDeviceBtn.addEventListener('click', async () => {
    const url = deviceIpInput.value.trim();
    try {
      await fetch('/api/config/device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: url })
      });
      deviceModal.classList.remove('active');
      fetchTelemetry();
    } catch (err) {
      alert('Failed to save device URL: ' + err.message);
    }
  });

  // ----------------- AI Chatbot -----------------
  async function sendChatMessage(msg) {
    if (!msg) return;

    // Append user message
    appendMessage(msg, 'user');
    chatInput.value = '';

    // Append thinking bubble
    const thinkingId = 'thinking-' + Date.now();
    const thinkingBubble = document.createElement('div');
    thinkingBubble.className = 'chat-bubble bot';
    thinkingBubble.id = thinkingId;
    thinkingBubble.textContent = 'Consulting agronomy knowledge base...';
    chatMessages.appendChild(thinkingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
      const resp = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      const data = await resp.json();
      document.getElementById(thinkingId)?.remove();
      appendMessage(data.reply || 'No response available.', 'bot');
    } catch (err) {
      document.getElementById(thinkingId)?.remove();
      appendMessage('Unable to reach assistant: ' + err.message, 'bot');
    }
  }

  function appendMessage(text, sender) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  sendChatBtn.addEventListener('click', () => sendChatMessage(chatInput.value.trim()));
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendChatMessage(chatInput.value.trim());
  });

  chatChips.forEach(chip => {
    chip.addEventListener('click', () => sendChatMessage(chip.textContent));
  });

  // Quick action from Dashboard card
  document.querySelectorAll('[data-goto]').forEach(el => {
    el.addEventListener('click', () => switchView(el.dataset.goto));
  });
});
