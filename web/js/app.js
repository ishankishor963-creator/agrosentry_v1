/**
 * app.js
 * ------
 * Client application controller for AgroSentry modern web frontend.
 * Features:
 * - Interactive Bioluminescent Particle Canvas Engine
 * - Interactive 3D Perspective Tilt on Cards
 * - Dynamic Liquid Soil Wave Height
 * - Liquid Gliding Pill Navigation Indicator
 * - Smooth Numerical Counter Ticker (requestAnimationFrame)
 * - Full Light Sensor Station (Lux, PPFD, DLI, spectral needle)
 * - ESP32 IP 192.168.31.57 Status Tracking
 */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation & Views
  const navBtns = document.querySelectorAll('.nav-btn');
  const navIndicator = document.getElementById('navIndicator');
  const sections = document.querySelectorAll('.view-section');
  let currentView = 'dashboard';

  // Sub-tabs (Camera vs Upload)
  const tabCameraBtn = document.getElementById('tabCameraBtn');
  const tabUploadBtn = document.getElementById('tabUploadBtn');
  const subTabIndicator = document.getElementById('subTabIndicator');
  const cameraMode = document.getElementById('cameraMode');
  const uploadMode = document.getElementById('uploadMode');

  // Camera Instance
  const camera = new window.FarmCamera('cameraVideo', 'snapshotCanvas');

  // Camera Action Buttons
  const snapBtn = document.getElementById('snapBtn');
  const switchCamBtn = document.getElementById('switchCamBtn');

  // Upload Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const previewBox = document.getElementById('previewBox');
  const previewImg = document.getElementById('previewImg');
  const analyzeUploadBtn = document.getElementById('analyzeUploadBtn');
  const clearUploadBtn = document.getElementById('clearUploadBtn');

  // Results Panel Elements
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

  // Spinner
  const scannerSpinner = document.getElementById('scannerSpinner');
  const spinnerText = document.getElementById('spinnerText');

  // Dashboard Telemetry Elements
  const valMoisture = document.getElementById('valMoisture');
  const valHumidity = document.getElementById('valHumidity');
  const valTemp = document.getElementById('valTemp');
  const valLight = document.getElementById('valLight');
  const badgeMoisture = document.getElementById('badgeMoisture');
  const badgeTemp = document.getElementById('badgeTemp');
  const badgeLight = document.getElementById('badgeLight');
  const moistureWaveBox = document.getElementById('moistureWaveBox');

  // Sensors View Telemetry Elements
  const sensorMoisture = document.getElementById('sensorMoisture');
  const sensorTemp = document.getElementById('sensorTemp');
  const sensorHumidity = document.getElementById('sensorHumidity');
  const sensorLight = document.getElementById('sensorLight');
  const valPPFD = document.getElementById('valPPFD');
  const valDLI = document.getElementById('valDLI');
  const spectrumNeedle = document.getElementById('spectrumNeedle');
  const lightConditionBadge = document.getElementById('lightConditionBadge');
  const lightAdvice = document.getElementById('lightAdvice');

  // Hardware Status & Modal
  const deviceStatusPill = document.getElementById('deviceStatusPill');
  const deviceDot = document.getElementById('deviceDot');
  const sonarRing = document.getElementById('sonarRing');
  const deviceText = document.getElementById('deviceText');
  const deviceModal = document.getElementById('deviceModal');
  const deviceIpInput = document.getElementById('deviceIpInput');
  const saveDeviceBtn = document.getElementById('saveDeviceBtn');
  const closeDeviceBtn = document.getElementById('closeDeviceBtn');

  // Alerts View Elements
  const droughtBadge = document.getElementById('droughtBadge');
  const droughtDesc = document.getElementById('droughtDesc');
  const floodBadge = document.getElementById('floodBadge');
  const floodDesc = document.getElementById('floodDesc');
  const solarBadge = document.getElementById('solarBadge');
  const solarDesc = document.getElementById('solarDesc');

  // Chat Elements
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendChatBtn = document.getElementById('sendChatBtn');
  const chatChips = document.querySelectorAll('.chat-chip');

  let selectedFileBase64 = null;
  const currentSensorValues = {
    moisture: 0,
    temp: 0,
    humidity: 0,
    light: 0,
    ppfd: 0,
    dli: 0
  };

  // ================= 1. BIOLUMINESCENT PARTICLE BACKGROUND =================
  const bgCanvas = document.getElementById('bgCanvas');
  const ctx = bgCanvas.getContext('2d');
  let width, height, particles = [];
  const mouse = { x: -1000, y: -1000, radius: 120 };

  function initCanvas() {
    width = bgCanvas.width = window.innerWidth;
    height = bgCanvas.height = window.innerHeight;
    particles = [];
    const count = Math.min(Math.floor((width * height) / 16000), 75);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.45,
        vy: (Math.random() - 0.5) * 0.45,
        size: Math.random() * 2.2 + 1,
        color: Math.random() > 0.4 ? 'rgba(139, 92, 246,' : (Math.random() > 0.5 ? 'rgba(34, 211, 238,' : 'rgba(52, 211, 153,'),
        alpha: Math.random() * 0.5 + 0.25
      });
    }
  }

  function renderParticles() {
    ctx.clearRect(0, 0, width, height);

    // Update & draw particles
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      // Mouse repulsion
      const dx = mouse.x - p.x;
      const dy = mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < mouse.radius) {
        const force = (mouse.radius - dist) / mouse.radius;
        p.x -= (dx / dist) * force * 3;
        p.y -= (dy / dist) * force * 3;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `${p.color} ${p.alpha})`;
      ctx.shadowBlur = 8;
      ctx.shadowColor = p.color + ' 0.8)';
      ctx.fill();

      // Connect filaments
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dxx = p.x - p2.x;
        const dyy = p.y - p2.y;
        const d = Math.sqrt(dxx * dxx + dyy * dyy);
        if (d < 95) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(139, 92, 246, ${0.18 * (1 - d / 95)})`;
          ctx.lineWidth = 0.8;
          ctx.shadowBlur = 0;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(renderParticles);
  }

  initCanvas();
  renderParticles();
  window.addEventListener('resize', initCanvas);
  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  // ================= 2. 3D INTERACTIVE TILT EFFECT =================
  const tiltCards = document.querySelectorAll('.metric-card, .glass-panel');
  tiltCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -6.5;
      const rotateY = ((x - centerX) / centerX) * 6.5;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });

  // ================= 3. LIQUID PILL NAVIGATION =================
  function updateNavIndicator(btn) {
    if (!btn || !navIndicator) return;
    navIndicator.style.width = `${btn.offsetWidth}px`;
    navIndicator.style.transform = `translateX(${btn.offsetLeft - 6}px)`;
  }

  function updateSubTabIndicator(btn) {
    if (!btn || !subTabIndicator) return;
    subTabIndicator.style.width = `${btn.offsetWidth}px`;
    subTabIndicator.style.transform = `translateX(${btn.offsetLeft - 4}px)`;
  }

  const initialActiveNav = document.querySelector('.nav-btn.active');
  if (initialActiveNav) setTimeout(() => updateNavIndicator(initialActiveNav), 60);

  const initialActiveSubTab = document.querySelector('.sub-tab-btn.active');
  if (initialActiveSubTab) setTimeout(() => updateSubTabIndicator(initialActiveSubTab), 60);

  function switchView(targetView) {
    currentView = targetView;
    navBtns.forEach(btn => {
      const isTarget = btn.dataset.view === targetView;
      btn.classList.toggle('active', isTarget);
      if (isTarget) updateNavIndicator(btn);
    });

    sections.forEach(sec => {
      sec.classList.toggle('active', sec.id === `view-${targetView}`);
    });

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

  // ================= 4. SCANNER SUB-TABS & CAMERA =================
  tabCameraBtn.addEventListener('click', () => {
    tabCameraBtn.classList.add('active');
    tabUploadBtn.classList.remove('active');
    updateSubTabIndicator(tabCameraBtn);
    cameraMode.style.display = 'block';
    uploadMode.style.display = 'none';
    camera.startStream();
  });

  tabUploadBtn.addEventListener('click', () => {
    tabUploadBtn.classList.add('active');
    tabCameraBtn.classList.remove('active');
    updateSubTabIndicator(tabUploadBtn);
    uploadMode.style.display = 'block';
    cameraMode.style.display = 'none';
    camera.stopStream();
  });

  snapBtn.addEventListener('click', async () => {
    const frameData = camera.captureFrame();
    if (!frameData) {
      alert('Camera stream is not ready. Please verify permissions.');
      return;
    }
    await runInference(frameData);
  });

  switchCamBtn.addEventListener('click', async () => {
    await camera.toggleFacingMode();
  });

  // ================= 5. FILE UPLOAD & DRAG/DROP =================
  dropZone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) handleImageFile(file);
  });

  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleImageFile(file);
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
      alert('Please select or drop a leaf image first.');
      return;
    }
    await runInference(selectedFileBase64);
  });

  // ================= 6. INFERENCE & DIAGNOSTIC RENDER =================
  async function runInference(imageBase64) {
    showSpinner('Running MobileNetV2 Neural Network Inference...');
    try {
      const resp = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: imageBase64 })
      });

      const data = await resp.json();
      if (!data.success) throw new Error(data.error || 'Diagnosis failed');

      renderDiagnosis(data.prediction);
    } catch (err) {
      console.error(err);
      alert('Error during diagnosis: ' + err.message);
    } finally {
      hideSpinner();
    }
  }

  function renderDiagnosis(pred) {
    resultPlaceholder.style.display = 'none';
    resultContent.style.display = 'block';

    if (pred.is_healthy) {
      resultBadge.className = 'result-badge badge-optimal';
      resultBadge.innerHTML = '<span>✅</span> Healthy Foliage';
      progressFill.className = 'progress-fill healthy';
    } else {
      resultBadge.className = 'result-badge badge-danger';
      resultBadge.innerHTML = '<span>⚠️</span> Infection Detected';
      progressFill.className = 'progress-fill disease';
    }

    resultTitle.textContent = pred.display_name;
    resultConfidence.textContent = `${pred.confidence}%`;
    progressFill.style.width = '0%';
    setTimeout(() => {
      progressFill.style.width = `${Math.min(pred.confidence, 100)}%`;
    }, 60);

    if (pred.inference_time_ms) {
      inferenceBadge.textContent = `⚡ Inference: ${pred.inference_time_ms} ms (MobileNetV2)`;
    }

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

    if (window.innerWidth < 960) {
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

  // ================= 7. SMOOTH NUMERICAL TICKER =================
  function animateValue(element, start, end, duration = 650, decimals = 1, isThousands = false) {
    if (!element) return;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      const current = start + (end - start) * ease;

      if (isThousands) {
        element.textContent = Math.round(current).toLocaleString();
      } else {
        element.textContent = current.toFixed(decimals);
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        if (isThousands) {
          element.textContent = Math.round(end).toLocaleString();
        } else {
          element.textContent = end.toFixed(decimals);
        }
      }
    }

    requestAnimationFrame(update);
  }

  // ================= 8. LIVE SENSORS POLLING & LIGHT STATION =================
  async function fetchTelemetry() {
    try {
      const resp = await fetch('/api/sensors');
      const data = await resp.json();

      // Animate Dashboard values
      animateValue(valMoisture, currentSensorValues.moisture, data.soil_moisture, 650, 1);
      animateValue(valHumidity, currentSensorValues.humidity, data.humidity, 650, 1);
      animateValue(valTemp, currentSensorValues.temp, data.temperature, 650, 1);
      animateValue(valLight, currentSensorValues.light, data.light_lux, 650, 0, true);

      // Animate Sensors View
      animateValue(sensorMoisture, currentSensorValues.moisture, data.soil_moisture, 650, 1);
      animateValue(sensorTemp, currentSensorValues.temp, data.temperature, 650, 1);
      animateValue(sensorHumidity, currentSensorValues.humidity, data.humidity, 650, 1);
      animateValue(sensorLight, currentSensorValues.light, data.light_lux, 650, 0, true);
      animateValue(valPPFD, currentSensorValues.ppfd, data.ppfd, 650, 1);
      animateValue(valDLI, currentSensorValues.dli, data.dli, 650, 1);

      // Dynamically adjust Liquid Wave height inside Moisture card
      if (moistureWaveBox) {
        const waveHeightPercent = Math.min(Math.max(data.soil_moisture * 0.9, 15), 88);
        moistureWaveBox.style.height = `${waveHeightPercent}%`;
      }

      // Update current values
      currentSensorValues.moisture = data.soil_moisture;
      currentSensorValues.humidity = data.humidity;
      currentSensorValues.temp = data.temperature;
      currentSensorValues.light = data.light_lux;
      currentSensorValues.ppfd = data.ppfd;
      currentSensorValues.dli = data.dli;

      // Status Badges
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

      // Light condition & moving spectral needle
      if (data.light_status === 'optimal') {
        badgeLight.className = 'metric-badge badge-solar';
        badgeLight.textContent = '● Full Photosynthesis';
        if (lightConditionBadge) {
          lightConditionBadge.className = 'metric-badge badge-solar';
          lightConditionBadge.textContent = '● Optimal Solar Radiation';
        }
      } else if (data.light_status === 'low') {
        badgeLight.className = 'metric-badge badge-warning';
        badgeLight.textContent = '▼ Low Irradiance';
        if (lightConditionBadge) {
          lightConditionBadge.className = 'metric-badge badge-warning';
          lightConditionBadge.textContent = '▼ Low Irradiance (Overcast)';
        }
      } else {
        badgeLight.className = 'metric-badge badge-danger';
        badgeLight.textContent = '▲ Scorching Sunlight';
        if (lightConditionBadge) {
          lightConditionBadge.className = 'metric-badge badge-danger';
          lightConditionBadge.textContent = '▲ Scorching Sunlight (High PAR)';
        }
      }

      if (spectrumNeedle) {
        const percent = Math.min(Math.max(((data.light_lux - 5000) / 75000) * 100, 4), 96);
        spectrumNeedle.style.left = `${percent}%`;
      }

      if (lightAdvice) {
        if (data.light_lux > 65000) {
          lightAdvice.textContent = 'Sunlight exceeds 65,000 Lux with high PAR levels. Consider deploying 30% shade cloth for young solanaceous seedlings to prevent photoinhibition and fruit sunscald.';
        } else if (data.light_lux < 15000) {
          lightAdvice.textContent = 'Ambient light is under 15,000 Lux. Photosynthesis is photon-limited. Ensure canopy is unshaded and adjust greenhouse shading louvers.';
        } else {
          lightAdvice.textContent = 'Current solar irradiance is within the prime photosynthetic saturation zone for tomatoes, peppers, potatoes, and field crops. Transpiration and stomatal conductance are optimal.';
        }
      }

      // Hardware status pill (ESP32 192.168.31.57)
      if (data.source.includes('192.168.31.57') || data.source.includes('ESP32') || data.source === 'device') {
        deviceDot.className = 'status-dot';
        if (sonarRing) sonarRing.className = 'sonar-ring';
        deviceText.textContent = 'ESP32 (192.168.31.57) Live';
      } else {
        deviceDot.className = 'status-dot amber';
        if (sonarRing) sonarRing.className = 'sonar-ring amber';
        deviceText.textContent = 'ESP32 (192.168.31.57) Listening';
      }
    } catch (e) {
      console.warn('Telemetry fetch error:', e);
    }
  }

  setInterval(fetchTelemetry, 3200);
  fetchTelemetry();

  // ================= 9. ALERTS =================
  async function fetchAlerts() {
    try {
      const resp = await fetch('/api/alerts');
      const data = await resp.json();

      droughtBadge.textContent = data.drought.level;
      droughtBadge.className = `metric-badge badge-${data.drought.level.toLowerCase() === 'normal' ? 'optimal' : (data.drought.level.toLowerCase() === 'critical' ? 'danger' : 'warning')}`;
      droughtDesc.textContent = data.drought.description;

      floodBadge.textContent = data.flood.level;
      floodBadge.className = `metric-badge badge-${data.flood.level.toLowerCase() === 'normal' ? 'optimal' : 'danger'}`;
      floodDesc.textContent = data.flood.description;

      if (currentSensorValues.light > 75000) {
        solarBadge.textContent = 'WARNING';
        solarBadge.className = 'metric-badge badge-warning';
        solarDesc.textContent = `Extreme solar radiation (${Math.round(currentSensorValues.light).toLocaleString()} Lux) detected. Deploy shade cloth to safeguard young foliage.`;
      } else {
        solarBadge.textContent = 'NORMAL';
        solarBadge.className = 'metric-badge badge-optimal';
        solarDesc.textContent = 'Solar radiation is within safe, non-scorching parameters for healthy leaf photosynthesis.';
      }
    } catch (e) {
      console.warn('Alerts fetch error:', e);
    }
  }

  // ================= 10. MODAL & CHAT =================
  deviceStatusPill.addEventListener('click', () => deviceModal.classList.add('active'));
  closeDeviceBtn.addEventListener('click', () => deviceModal.classList.remove('active'));

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

  async function sendChatMessage(msg) {
    if (!msg) return;
    appendMessage(msg, 'user');
    chatInput.value = '';

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

  document.querySelectorAll('[data-goto]').forEach(el => {
    el.addEventListener('click', () => switchView(el.dataset.goto));
  });
});
