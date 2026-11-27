/**
 * Module Đặt lịch & Quản lý Ghế trống (Capacity Management) - Nha Khoa Minh Sinh
 * File: wordpress/wp-content/themes/minhsinh-dental/js/booking-capacity.js
 */
(function () {
  'use strict';

  // State quản lý nội bộ
  let abortController = null;
  let debounceTimer = null;
  let lastCheckData = null;
  let lastDistributeData = null;
  let isAutoDistributeChecked = true;

  // --- 1. INJECT RESPONSIVE FLUID CSS ---
  function injectStyles() {
    if (document.getElementById('ms-capacity-styles')) return;

    const styleEl = document.createElement('style');
    styleEl.id = 'ms-capacity-styles';
    styleEl.textContent = `
      /* Reset Box-Sizing & Fluid Base */
      .ms-capacity-container,
      .ms-capacity-container * {
        box-sizing: border-box;
        min-width: 0;
      }

      .ms-capacity-container {
        width: 100%;
        margin-top: clamp(12px, 2vw, 20px);
        font-family: inherit;
        overflow-x: hidden;
      }

      /* Badges & Banners */
      .ms-banner-badge {
        display: flex;
        align-items: center;
        gap: clamp(8px, 1.5vw, 12px);
        padding: clamp(10px, 1.5vw, 14px) clamp(12px, 2vw, 18px);
        border-radius: 8px;
        font-size: clamp(13px, 1.2vw, 15px);
        font-weight: 500;
        line-height: 1.4;
        transition: all 0.3s ease;
        width: 100%;
        word-break: break-word;
      }

      .ms-badge-green {
        background-color: #e6f4ea;
        color: #137333;
        border: 1px solid #ceead6;
      }

      .ms-badge-orange {
        background-color: #feefc3;
        color: #b06000;
        border: 1px solid #fde293;
      }

      .ms-badge-red {
        background-color: #fce8e6;
        color: #c5221f;
        border: 1px solid #fad2cf;
      }

      .ms-badge-icon {
        flex-shrink: 0;
        width: 20px;
        height: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }

      /* Step 3 Capacity Panel */
      .ms-distribute-panel {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: clamp(14px, 2.5vw, 20px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        width: 100%;
      }

      .ms-warning-box {
        padding: clamp(10px, 1.8vw, 14px);
        border-radius: 6px;
        margin-bottom: 14px;
        font-size: clamp(13px, 1.1vw, 14.5px);
        word-break: break-word;
      }

      .ms-checkbox-label {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        cursor: pointer;
        user-select: none;
        font-weight: 600;
        font-size: clamp(13.5px, 1.2vw, 15px);
        color: #2c3e50;
        margin-bottom: 16px;
        word-break: break-word;
      }

      .ms-checkbox-label input[type="checkbox"] {
        width: 18px;
        height: 18px;
        margin-top: 2px;
        cursor: pointer;
        accent-color: #0066cc;
        flex-shrink: 0;
      }

      /* Distribution Preview Grid & List */
      .ms-summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: clamp(8px, 1.5vw, 12px);
        margin-bottom: 16px;
        width: 100%;
      }

      .ms-summary-card {
        background: #f8f9fa;
        border: 1px solid #eaedd0;
        border-left: 4px solid #0066cc;
        padding: 10px 12px;
        border-radius: 6px;
        font-size: clamp(12.5px, 1vw, 13.5px);
        word-break: break-word;
      }

      .ms-patients-preview-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
      }

      .ms-patient-preview-item {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        padding: 10px 12px;
        background: #fafafa;
        border: 1px solid #eee;
        border-radius: 6px;
        font-size: clamp(12.5px, 1.1vw, 14px);
        width: 100%;
      }

      .ms-patient-info {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        font-weight: 500;
        min-width: 0;
        flex: 1;
      }

      .ms-time-tag {
        background: #0066cc;
        color: #fff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
      }

      /* Result Screen Styles */
      .ms-result-auto-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #0d47a1;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin: 10px 0;
      }

      .ms-result-patient-table-wrapper {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin-top: 12px;
      }

      .ms-result-patient-table {
        width: 100%;
        border-collapse: collapse;
        min-width: 320px;
      }

      .ms-result-patient-table th, 
      .ms-result-patient-table td {
        padding: 8px 12px;
        border: 1px solid #e0e0e0;
        text-align: left;
        font-size: clamp(12px, 1.1vw, 14px);
        word-break: break-word;
      }

      .ms-result-patient-table th {
        background: #f5f5f5;
      }

      /* Responsive Media Breakpoints */
      @media (min-width: 1280px) {
        .ms-capacity-container {
          max-width: 100%;
        }
      }

      @media (min-width: 768px) and (max-width: 1024px) {
        .ms-summary-grid {
          grid-template-columns: repeat(2, 1fr);
        }
      }

      @media (max-width: 767px) {
        .ms-patient-preview-item {
          flex-direction: column;
          align-items: flex-start;
        }
        .ms-summary-grid {
          grid-template-columns: 1fr;
        }
        .ms-banner-badge {
          flex-direction: column;
          align-items: flex-start;
        }
      }

      @media (max-width: 414px) {
        .ms-capacity-container {
          padding-left: 4px;
          padding-right: 4px;
        }
        .ms-distribute-panel {
          padding: 10px;
        }
      }
    `;
    document.head.appendChild(styleEl);
  }

  // --- 2. INTEGRATION WITH DOM ---
  function getOrCreateElement(id, parentSelector, insertAfterSelector, className) {
    let el = document.getElementById(id);
    if (!el) {
      const parent = document.querySelector(parentSelector);
      if (!parent) return null;

      el = document.createElement('div');
      el.id = id;
      if (className) el.className = className;

      const targetAfter = insertAfterSelector ? parent.querySelector(insertAfterSelector) : null;
      if (targetAfter && targetAfter.parentNode) {
        targetAfter.parentNode.insertBefore(el, targetAfter.nextSibling);
      } else {
        parent.appendChild(el);
      }
    }
    return el;
  }

  function getStep2Container() {
    return getOrCreateElement('msCapacityBannerStep2', '#paneStep2', '#timeSlotsGrid, #selectedTimeInfo', 'ms-capacity-container');
  }

  function getStep3Container() {
    return getOrCreateElement('msCapacityPanelStep3', '#paneStep3', '#patientsListContainer', 'ms-capacity-container');
  }

  // --- HELPER: EXTRACT DATA FROM DOM ---
  function getBookingParamsFromDOM() {
    // 2. Extract clinic_id chuẩn
    const activeClinic = document.querySelector('#clinicsTabs .active, #clinicsTabs [data-active=true], input[name=clinic_id]:checked');
    const clinicId = activeClinic ? (activeClinic.dataset.clinicId || activeClinic.value || window.__msBookingData?.clinicId) : (window.__msBookingData?.clinicId || '1');

    // Date
    const dateInput = document.querySelector('#bookingDate');
    const date = dateInput ? dateInput.value : new Date().toISOString().split('T')[0];

    // 1. Extract start_time chuẩn
    const activeSlot = document.querySelector('#timeSlotsGrid .time-slot.selected, #timeSlotsGrid .active');
    const rawTime = activeSlot ? (activeSlot.dataset.time || activeSlot.textContent || '') : '';
    const timeMatch = rawTime.match(/\b(\d{2}:\d{2})\b/);
    const startTime = timeMatch ? timeMatch[1] : '';

    // 3. Extract patient cards trong #patientsListContainer .patient-card
    const patientCards = document.querySelectorAll('#patientsListContainer .patient-card');
    const patients = [];

    patientCards.forEach((card, idx) => {
      const nameInput = card.querySelector('.p-name, .patient-name, input[name*=name]');
      const serviceSelect = card.querySelector('.p-service, .patient-service, select[name*=service]');
      const timeSelect = card.querySelector('.p-time, select[name*=time]');
      const durationInput = card.querySelector('input[name*=duration]');

      let estimateDuration = 30;
      if (serviceSelect && serviceSelect.options && serviceSelect.selectedIndex >= 0) {
        const selectedOpt = serviceSelect.options[serviceSelect.selectedIndex];
        estimateDuration = parseInt(selectedOpt?.dataset?.estimate, 10) || 30;
      }
      const duration = durationInput ? parseInt(durationInput.value, 10) : estimateDuration;

      patients.push({
        id: card.dataset.id || `patient_${idx + 1}`,
        guest_number: idx + 1,
        guest_label: 'Khách ' + (idx + 1),
        name: nameInput ? (nameInput.value || nameInput.textContent.trim()) : `Khách ${idx + 1}`,
        service_id: serviceSelect ? serviceSelect.value : '',
        service_name: serviceSelect && serviceSelect.options && serviceSelect.selectedIndex >= 0 ? (serviceSelect.options[serviceSelect.selectedIndex]?.text || '') : '',
        time: timeSelect ? timeSelect.value : '',
        duration: duration
      });
    });

    // Fallback khi không có patient card nào trong DOM (ví dụ ở Step 2)
    let totalPassengerCount = 1;
    let totalDuration = 30;

    if (patients.length > 0) {
      totalPassengerCount = patients.length;
      totalDuration = patients.reduce((acc, p) => acc + (p.duration || 30), 0);
    } else {
      const mainServiceSelect = document.querySelector('#mainServiceSelect');
      if (mainServiceSelect && mainServiceSelect.options && mainServiceSelect.selectedIndex >= 0) {
        const mainOpt = mainServiceSelect.options[mainServiceSelect.selectedIndex];
        totalDuration = parseInt(mainOpt?.dataset?.estimate, 10) || 30;
      }
      patients.push({ 
        id: 'p1', 
        guest_number: 1, 
        guest_label: 'Khách 1', 
        name: 'Khách 1', 
        duration: totalDuration 
      });
    }

    return {
      clinic_id: parseInt(clinicId, 10) || 1,
      date: date,
      start_time: startTime,
      patients: patients,
      passenger_count: totalPassengerCount,
      duration: totalDuration
    };
  }

  // --- 3. API CALLS WITH DEBOUNCE & ABORT CONTROLLER ---
  function triggerSync(bookingData) {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      executeSync(bookingData);
    }, 200);
  }

  async function executeSync(bookingData) {
    const domParams = getBookingParamsFromDOM();
    let params = domParams;

    if (bookingData && typeof bookingData === 'object') {
      const rawTimeInput = bookingData.start_time || bookingData.time || domParams.start_time;
      const timeMatch = typeof rawTimeInput === 'string' ? rawTimeInput.match(/\b(\d{2}:\d{2})\b/) : null;
      const resolvedStartTime = timeMatch ? timeMatch[1] : domParams.start_time;

      const resolvedPatients = (Array.isArray(bookingData.patients) && bookingData.patients.length > 0) 
        ? bookingData.patients.map((p, idx) => ({
            ...p,
            guest_number: p.guest_number || (idx + 1),
            guest_label: p.guest_label || ('Khách ' + (idx + 1))
          }))
        : domParams.patients;

      params = {
        clinic_id: parseInt(bookingData.clinic_id ?? bookingData.clinicId ?? domParams.clinic_id, 10) || 1,
        date: bookingData.date || domParams.date,
        start_time: resolvedStartTime,
        patients: resolvedPatients,
        passenger_count: bookingData.passenger_count || (resolvedPatients.length > 0 ? resolvedPatients.length : domParams.passenger_count),
        duration: bookingData.duration || domParams.duration
      };
    }

    if (!params.start_time || !params.date) return;

    if (abortController) {
      abortController.abort();
    }
    abortController = new AbortController();

    try {
      // 1. GET Capacity Check
      const queryStr = new URLSearchParams({
        clinic_id: params.clinic_id,
        date: params.date,
        start_time: params.start_time,
        passenger_count: params.passenger_count,
        duration: params.duration
      }).toString();

      const capacityRes = await fetch(`/api/capacity-check/?${queryStr}`, {
        signal: abortController.signal
      });

      if (!capacityRes.ok) throw new Error('Network error capacity-check');
      const capacityData = await capacityRes.json();
      lastCheckData = capacityData;

      // Render Step 2 Banner
      renderStep2Banner(capacityData, params);

      // 2. Yêu cầu b: Kiểm tra điều kiện thiếu ghế hoặc số khách > 5
      const availableChairs = capacityData.available_chairs ?? 0;
      const isInsufficient = (availableChairs < params.passenger_count) || (params.passenger_count > 5) || capacityData.is_full || !capacityData.is_available;

      if (isInsufficient) {
        let distributeData = null;
        try {
          // POST Distribute Preview
          const previewRes = await fetch('/api/capacity-distribute/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              clinic_id: params.clinic_id,
              date: params.date,
              start_time: params.start_time,
              patients: params.patients,
              passenger_count: params.passenger_count,
              duration: params.duration
            }),
            signal: abortController.signal
          });

          if (!previewRes.ok) throw new Error('Network error capacity-distribute');
          distributeData = await previewRes.json();
        } catch (apiErr) {
          // Fallback preview từ danh sách slot còn mở trên DOM nếu API lỗi hoặc không trả về distributed_patients
          console.warn('[MS Booking Capacity] API distribute error, generating fallback preview:', apiErr);
          const openSlotElements = document.querySelectorAll('#timeSlotsGrid .time-slot:not(.disabled)');
          const openTimes = Array.from(openSlotElements).map(el => {
            const tText = el.dataset.time || el.textContent || '';
            const m = tText.match(/\b(\d{2}:\d{2})\b/);
            return m ? m[1] : null;
          }).filter(Boolean);

          let currentOpenIdx = 0;
          const fallbackPatients = params.patients.map((p, idx) => {
            const assignedTime = openTimes[currentOpenIdx] || params.start_time;
            if (openTimes.length > 0 && currentOpenIdx < openTimes.length - 1) {
              currentOpenIdx++;
            }
            return {
              ...p,
              assigned_time: assignedTime,
              start_time: assignedTime
            };
          });

          distributeData = {
            needs_distribution: true,
            can_fulfill_all: openTimes.length > 0,
            warning_message: params.passenger_count > 5 
              ? 'Số lượng khách vượt quá giới hạn tối đa (5 khách). Hệ thống đã tự động sắp xếp phân bổ sang các khung giờ lân cận.' 
              : 'Số lượng ghế trống trong khung giờ chọn không đủ cho tất cả khách. Đã tự động phân bổ dự kiến.',
            distribution_summary: [{ time: params.start_time, count: Math.min(params.passenger_count, availableChairs || 1) }],
            distributed_patients: fallbackPatients,
            unassigned_count: 0
          };
        }

        lastDistributeData = distributeData;

        // Render Step 3 Panel
        renderStep3Panel(distributeData, params);

        // Xử lý tự động sắp xếp lịch nếu checkbox được bật và có danh sách phân bổ
        if (isAutoDistributeChecked && distributeData && Array.isArray(distributeData.distributed_patients) && distributeData.distributed_patients.length > 0) {
          const patientCards = document.querySelectorAll('#patientsListContainer .patient-card');
          distributeData.distributed_patients.forEach((dp, idx) => {
            if (patientCards[idx]) {
              const timeSelect = patientCards[idx].querySelector('.p-time, select[name*=time]');
              const targetTime = dp.assigned_time || dp.start_time;
              if (timeSelect && targetTime) {
                timeSelect.value = targetTime;
                timeSelect.dispatchEvent(new Event('change', { bubbles: true }));
              }
            }
          });

          // Dispatch Custom Event để page-booking.php refresh lại trạng thái disabled của các dropdown .p-time
          window.dispatchEvent(new CustomEvent('ms:capacityDistributed', {
            detail: { distributed_patients: distributeData.distributed_patients }
          }));
        }

      } else {
        lastDistributeData = null;
        clearStep3Panel();
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('[MS Booking Capacity] Error:', err);
      }
    }
  }

  // --- RENDER FUNCTIONS ---
  function renderStep2Banner(data, params) {
    const container = getStep2Container();
    if (!container) return;

    const available = data.available_chairs ?? 0;
    const total = data.total_chairs ?? 0;
    const count = params.passenger_count;
    const isEnough = (available >= count) && (count <= 5) && !data.is_full && data.is_available;

    let badgeClass = 'ms-badge-green';
    let icon = '✓';
    let message = `Còn <strong>${available}/${total}</strong> ghế trống tại ${params.start_time}`;

    if (!isEnough) {
      if (count > 5) {
        badgeClass = 'ms-badge-red';
        icon = '⛔';
        message = `Số lượng khách (${count}) vượt quá giới hạn tối đa cho phép (5 khách/lượt). Khung giờ sẽ được tự động phân bổ sang các mốc giờ kế tiếp.`;
      } else if (available > 0) {
        badgeClass = 'ms-badge-orange';
        icon = '⚠️';
        message = `Chỉ còn <strong>${available}/${total}</strong> ghế trống tại ${params.start_time} (Yêu cầu: ${count} ghế). Hệ thống sẽ tự động phân bổ lịch.`;
      } else {
        badgeClass = 'ms-badge-red';
        icon = '✕';
        message = `Khung giờ ${params.start_time} đã hết ghế trống (0/${total}). Hệ thống sẽ phân phối sang giờ khác.`;
      }
    }

    container.innerHTML = `
      <div class="ms-banner-badge ${badgeClass}">
        <span class="ms-badge-icon">${icon}</span>
        <span>${message}</span>
      </div>
    `;
  }

  function renderStep3Panel(data, params) {
    const container = getStep3Container();
    if (!container) return;

    if (typeof data.needs_distribution !== 'undefined' && typeof data.can_fulfill_all !== 'undefined') {
      isAutoDistributeChecked = data.needs_distribution && data.can_fulfill_all;
    }

    const passengerCount = (params && params.passenger_count) || (params && params.patients && params.patients.length) || 0;
    const unassignedCount = data.unassigned_count || 0;
    const isOverLimit = Boolean((params && params.passenger_count > 5) || unassignedCount > 0 || !data.can_fulfill_all);
    const topBadgeClass = isOverLimit ? 'ms-badge-red' : 'ms-badge-orange';
    const topBadgeIcon = isOverLimit ? '⛔' : '⚠️';

    let topBannerMessage = '';
    if (params && params.passenger_count > 5) {
      topBannerMessage = `Hiện có <strong>${passengerCount} khách</strong> (vượt quá mức tối đa 5 khách/lượt). Hệ thống đã tự động kích hoạt điều phối và phân bổ lịch sang các khung giờ kế tiếp.`;
    } else if (!data.can_fulfill_all || unassignedCount > 0) {
      topBannerMessage = `Hiện có <strong>${passengerCount} khách</strong>, vượt quá số ghế còn trống tại khung giờ đã chọn và không đủ ghế trong ngày (còn thiếu cho <strong>${unassignedCount}</strong> khách). Lịch đang được phân phối sang các khung giờ kế tiếp.`;
    } else {
      topBannerMessage = `Hiện có <strong>${passengerCount} khách</strong>, vượt quá số ghế còn trống tại khung giờ đã chọn. Hệ thống đang tự động phân bổ lịch hẹn sang các khung giờ kế tiếp.`;
    }

    const defaultWarning = params && params.passenger_count > 5 
      ? 'Số lượng khách vượt quá 5 người. Đã kích hoạt cơ chế tự động phân bổ lịch.' 
      : 'Số lượng ghế trống trong khung giờ chọn không đủ cho tất cả khách.';
    const warningMsg = data.warning_message || defaultWarning;
    const summaryList = data.distribution_summary || [];
    const patientList = data.distributed_patients || [];

    let summaryHtml = '';
    if (summaryList.length > 0) {
      summaryHtml = `
        <div class="ms-summary-grid">
          ${summaryList.map(item => `
            <div class="ms-summary-card">
              <strong>${item.time || item.start_time}:</strong> ${item.count || item.patient_count} khách
            </div>
          `).join('')}
        </div>
      `;
    }

    let patientsHtml = '';
    if (patientList.length > 0) {
      patientsHtml = `
        <div class="ms-patients-preview-list">
          ${patientList.map((p, idx) => {
            const guestNum = p.guest_number || (idx + 1);
            const rawPatientName = p.name || p.patient_name || '';
            const displayName = rawPatientName ? ('Khách ' + guestNum + ': ' + rawPatientName) : ('Khách ' + guestNum);
            return `
            <div class="ms-patient-preview-item">
              <div class="ms-patient-info">
                <span>👤 <strong>${displayName}</strong></span>
                ${p.service_name ? `<small style="color:#666;">(${p.service_name})</small>` : ''}
              </div>
              <div>
                <span class="ms-time-tag">Giờ mới: ${p.assigned_time || p.start_time}</span>
              </div>
            </div>
          `;
          }).join('')}
        </div>
      `;
    }

    let unassignedHtml = '';
    if (!data.can_fulfill_all || unassignedCount > 0) {
      unassignedHtml = `
        <div class="ms-banner-badge ms-badge-red" style="margin-top: 12px;">
          <span class="ms-badge-icon">⛔</span>
          <span>Cảnh báo: Không đủ ghế phục vụ cho <strong>${unassignedCount}</strong> khách trong ngày này!</span>
        </div>
      `;
    }

    container.innerHTML = `
      <div class="ms-distribute-panel">
        <div class="ms-banner-badge ${topBadgeClass}" style="margin-bottom: 14px;">
          <span class="ms-badge-icon">${topBadgeIcon}</span>
          <span>${topBannerMessage}</span>
        </div>
        <div class="ms-warning-box ms-badge-orange">
          ⚠️ ${warningMsg}
        </div>
        <label class="ms-checkbox-label">
          <input type="checkbox" id="msAutoDistributeCheckbox" ${isAutoDistributeChecked ? 'checked' : ''} />
          <span>Tự động phân phối lịch sang các khung giờ kế tiếp</span>
        </label>
        ${summaryHtml}
        ${patientsHtml}
        ${unassignedHtml}
      </div>
    `;

    // Bind checkbox state
    const cb = document.getElementById('msAutoDistributeCheckbox');
    if (cb) {
      cb.addEventListener('change', (e) => {
        isAutoDistributeChecked = e.target.checked;
      });
    }
  }

  function clearStep3Panel() {
    const container = document.getElementById('msCapacityPanelStep3');
    if (container) container.innerHTML = '';
  }

  // --- 4. EXPOSE WINDOW OBJECT ---
  window.MSBookingCapacity = {
    sync: function (bookingData) {
      triggerSync(bookingData);
    },

    getAutoDistribute: function () {
      const cb = document.getElementById('msAutoDistributeCheckbox');
      if (cb) return cb.checked;
      return isAutoDistributeChecked;
    },

    getLastCheck: function () {
      return {
        capacity: lastCheckData,
        distribute: lastDistributeData
      };
    },

    renderBookingResult: function (resData, summaryEl, groupCodeEl, bookingData, servicesList) {
      if (groupCodeEl && (resData.pnr_code || resData.group_code)) {
        groupCodeEl.textContent = resData.pnr_code || resData.group_code;
      }

      if (!summaryEl) return;

      let html = '';

      if (resData.auto_distributed === true) {
        html += `
          <div class="ms-result-auto-badge">
            ✨ Đã tự động phân phối sang nhiều khung giờ
          </div>
        `;
      }

      const bookings = resData.bookings || [];
      if (bookings.length > 0) {
        html += `
          <div class="ms-result-patient-table-wrapper">
            <table class="ms-result-patient-table">
              <thead>
                <tr>
                  <th>Khách hàng</th>
                  <th>Dịch vụ</th>
                  <th>Giờ hẹn thực tế</th>
                </tr>
              </thead>
              <tbody>
                ${bookings.map((b, idx) => {
                  const guestNum = idx + 1;
                  const rawName = b.patient_name || b.customer_name || b.full_name || b.fullName || b.name || '';
                  const patientName = rawName ? ('Khách ' + guestNum + ': ' + rawName) : ('Khách ' + guestNum);
                  
                  const matchedService = Array.isArray(servicesList) && b.category_id
                    ? servicesList.find(s => String(s.id || s.category_id) === String(b.category_id))
                    : null;
                  const serviceName = b.service_name || b.service || b.category_name || (matchedService ? matchedService.name : '') || '-';
                  const startTime = b.start_time || b.assigned_time || b.time || '';
                  return `
                  <tr>
                    <td><strong>${patientName}</strong></td>
                    <td>${serviceName}</td>
                    <td><span class="ms-time-tag">${startTime}</span></td>
                  </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        `;
      } else {
        html += `<p>Đặt lịch thành công!</p>`;
      }

      summaryEl.innerHTML = html;
    }
  };

  // --- 5. AUTOMATIC LISTENERS & OBSERVERS ---
  function initAutoListeners() {
    injectStyles();

    // 5. Event listeners trong initAutoListeners()
    // Click delegation bắt thêm các phần tử tương tác
    document.addEventListener('click', (e) => {
      if (e.target.closest('#clinicsTabs .clinic-tab-btn, #clinicsTabs [data-clinic-id], #timeSlotsGrid .time-slot, #btnAddCompanion, .btn-remove-patient')) {
        setTimeout(() => triggerSync(), 50);
      }
    });

    // Change delegation bắt thêm các input/select cấu hình
    document.addEventListener('change', (e) => {
      if (e.target.closest('#mainServiceSelect, #bookingDate, #clinicsTabs input, #patientsListContainer select, #patientsListContainer input')) {
        triggerSync();
      }
    });

    // Input delegation (với debounce) cho tên khách hàng
    document.addEventListener('input', (e) => {
      if (e.target.closest('#patientsListContainer .p-name, #patientsListContainer .patient-name')) {
        triggerSync();
      }
    });

    // MutationObserver on #patientsListContainer
    const observerTarget = document.getElementById('patientsListContainer');
    if (observerTarget) {
      const observer = new MutationObserver(() => {
        triggerSync();
      });
      observer.observe(observerTarget, { childList: true, subtree: true });
    }

    // Initial Trigger if elements exist
    if (document.querySelector('#timeSlotsGrid')) {
      triggerSync();
    }
  }

  // Initialize on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAutoListeners);
  } else {
    initAutoListeners();
  }
})();