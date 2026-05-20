// ━━━━━━━━━━ 編輯材料 ━━━━━━━━━━

const materialId = document.getElementById('materialId').value;
let originalData = null;

async function loadCategorySelect() {
  const res = await fetch('/api/categories');
  const cats = await res.json();
  const sel = document.getElementById('categorySelect');
  sel.innerHTML = cats.map(c => `<option value="${c.id}" data-prefix="${c.code_prefix}">${c.name}</option>`).join('');
}

async function loadMaterial() {
  const res = await fetch('/api/materials/' + materialId);
  if (!res.ok) {
    document.getElementById('footStatus').textContent = '載入失敗';
    return;
  }
  const m = await res.json();
  originalData = m;

  // 填表
  document.getElementById('codeDisplay').textContent = m.code;
  document.getElementById('editingCode').textContent = '編號:' + m.code;
  document.getElementById('categorySelect').value = m.category_id;
  document.getElementById('subcategoryInput').value = m.subcategory || '';
  document.getElementById('nameInput').value = m.name || '';
  document.getElementById('statusSelect').value = m.status || '常用';
  document.getElementById('specInput').value = m.spec || '';
  document.getElementById('detailInput').value = m.detail || '';
  document.getElementById('unitSelect').value = m.unit || '才';
  document.getElementById('priceMaterialInput').value = m.price_material || '';
  document.getElementById('priceLaborInput').value = m.price_labor || '';
  document.getElementById('priceUpdated').value = m.price_updated || '';
  document.getElementById('supplierInput').value = m.supplier || '';
  document.getElementById('supplierContactInput').value = m.supplier_contact || '';
  document.getElementById('brandInput').value = m.brand || '';
  document.getElementById('modelInput').value = m.model || '';
  document.getElementById('clientAboutInput').value = m.client_about || '';
  document.getElementById('clientCareInput').value = m.client_care || '';
  document.getElementById('internalNoteInput').value = m.internal_note || '';
  document.getElementById('bugNoteInput').value = m.bug_note || '';
  document.getElementById('usageLocationsInput').value = m.usage_locations || '';
  document.getElementById('tagsInput').value = m.tags || '';

  // 單位附加字
  updatePriceUnit();

  // 載入照片預覽
  if (m.photo_main) {
    showPhotoPreview('photoMainBox', '/photos/' + m.photo_main, 'main', 'remove_photo_main');
  }
  if (m.photo_subs) {
    const subs = m.photo_subs.split(',').filter(Boolean);
    subs.forEach(p => {
      // 偵測是 sub_1 / sub_2 / sub_3
      const match = p.match(/sub_(\d)/);
      if (match) {
        const i = match[1];
        showPhotoPreview(`photoSub${i}Box`, '/photos/' + p, `sub_${i}`, `remove_photo_sub_${i}`);
      }
    });
  }

  document.getElementById('footStatus').textContent = '已載入,可開始編輯';
}

function showPhotoPreview(boxId, imgSrc, photoKey, removeFieldId) {
  const box = document.getElementById(boxId);
  box.classList.add('has-image');
  box.innerHTML = `
    <button type="button" class="remove-btn" onclick="removePhoto('${boxId}', '${photoKey}', '${removeFieldId}', event)">✕</button>
    <img src="${imgSrc}" />
    <input type="file" name="photo_${photoKey}" accept="image/*" style="display:none;" onchange="previewPhoto(this, '${boxId}', '${photoKey}')" />
  `;
}

function previewPhoto(input, boxId, photoKey) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = e => {
    const box = document.getElementById(boxId);
    box.classList.add('has-image');
    box.innerHTML = `
      <button type="button" class="remove-btn" onclick="removePhoto('${boxId}', '${photoKey}', 'remove_photo_${photoKey}', event)">✕</button>
      <img src="${e.target.result}" />
      <input type="file" name="photo_${photoKey}" accept="image/*" style="display:none;" onchange="previewPhoto(this, '${boxId}', '${photoKey}')" />
    `;
    const newInput = box.querySelector('input[type="file"]');
    const dt = new DataTransfer();
    dt.items.add(file);
    newInput.files = dt.files;
    // 清除 remove flag
    const removeField = document.getElementById('remove_photo_' + photoKey === 'remove_photo_main' ? 'removeMain' : 'removeSub' + photoKey.split('_')[1]);
    if (removeField) removeField.value = '0';
  };
  reader.readAsDataURL(file);
}

function removePhoto(boxId, photoKey, removeFieldName, event) {
  event.preventDefault();
  event.stopPropagation();
  if (!confirm('確定要刪除這張照片?')) return;
  const box = document.getElementById(boxId);
  const isMain = photoKey === 'main';
  const labelText = isMain ? '點擊上傳' : '加圖';

  box.classList.remove('has-image');
  box.innerHTML = `
    <span class="photo-box-icon">＋</span>
    <span class="photo-box-text">${labelText}</span>
    <input type="file" name="photo_${photoKey}" accept="image/*" style="display:none;" onchange="previewPhoto(this, '${boxId}', '${photoKey}')" />
  `;

  // 設定刪除 flag
  let removeFieldId;
  if (photoKey === 'main') removeFieldId = 'removeMain';
  else removeFieldId = 'removeSub' + photoKey.split('_')[1];
  document.getElementById(removeFieldId).value = '1';
}

function updatePriceUnit() {
  const u = document.getElementById('unitSelect').value;
  document.getElementById('priceUnit').textContent = '元 / ' + u;
  document.getElementById('priceUnit2').textContent = '元 / ' + u;
}

document.getElementById('unitSelect').addEventListener('change', updatePriceUnit);

// note tabs
document.querySelectorAll('.note-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.note-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.querySelectorAll('.note-area').forEach(a => a.style.display = 'none');
    document.getElementById('noteArea_' + tab.dataset.target).style.display = 'block';
  });
});

// 提交 — 用 PUT
document.getElementById('materialForm').addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  document.getElementById('footStatus').textContent = '儲存中…';
  try {
    const res = await fetch('/api/materials/' + materialId, {method: 'PUT', body: fd});
    const data = await res.json();
    if (data.ok) {
      document.getElementById('footStatus').textContent = '已儲存,返回中…';
      setTimeout(() => window.location.href = '/', 600);
    } else {
      alert('儲存失敗:' + (data.error || ''));
      document.getElementById('footStatus').textContent = '儲存失敗';
    }
  } catch (err) {
    alert('錯誤:' + err.message);
  }
});

// 刪除
document.getElementById('deleteBtn').addEventListener('click', async () => {
  if (!originalData) return;
  const confirmText = `確定要刪除「${originalData.name}」(${originalData.code})?\n\n這個動作不能還原,連同照片也會一起刪除。`;
  if (!confirm(confirmText)) return;
  // 二次確認
  if (!confirm('再次確認:刪除後無法復原,確定要刪除?')) return;

  document.getElementById('footStatus').textContent = '刪除中…';
  const res = await fetch('/api/materials/' + materialId, {method: 'DELETE'});
  const data = await res.json();
  if (data.ok) {
    document.getElementById('footStatus').textContent = '已刪除';
    setTimeout(() => window.location.href = '/', 400);
  } else {
    alert('刪除失敗:' + (data.error || ''));
  }
});

// 啟動
(async () => {
  await loadCategorySelect();
  await loadMaterial();
})();
