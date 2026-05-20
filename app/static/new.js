// ━━━━━━━━━━ 新增材料表單 ━━━━━━━━━━

// 載入分類選單
async function loadCategorySelect() {
  const res = await fetch('/api/categories');
  const cats = await res.json();
  const sel = document.getElementById('categorySelect');
  sel.innerHTML = cats.map(c => `<option value="${c.id}" data-prefix="${c.code_prefix}">${c.name}</option>`).join('');

  // 觸發初始編號
  await updateCode();

  sel.addEventListener('change', updateCode);
}

async function updateCode() {
  const sel = document.getElementById('categorySelect');
  const catId = sel.value;
  if (!catId) return;
  const res = await fetch('/api/next-code/' + catId);
  const data = await res.json();
  document.getElementById('codePreview').textContent = data.code || '—';
}

// 單位變化時,單價單位也要跟著變
document.querySelector('select[name="unit"]').addEventListener('change', e => {
  const u = e.target.value;
  document.getElementById('priceUnit').textContent = '元 / ' + u;
  document.getElementById('priceUnit2').textContent = '元 / ' + u;
});

// 照片預覽
function previewPhoto(input, boxId) {
  if (!input.files || !input.files[0]) return;
  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = e => {
    const box = document.getElementById(boxId);
    box.classList.add('has-image');
    box.innerHTML = `<img src="${e.target.result}" /><input type="file" name="${input.name}" accept="image/*" style="display:none;" onchange="previewPhoto(this, '${boxId}')" />`;
    // 重新綁定 file 物件
    const newInput = box.querySelector('input[type="file"]');
    const dt = new DataTransfer();
    dt.items.add(file);
    newInput.files = dt.files;
  };
  reader.readAsDataURL(file);
}

// note tabs 切換
document.querySelectorAll('.note-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.note-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.querySelectorAll('.note-area').forEach(a => a.style.display = 'none');
    document.getElementById('noteArea_' + tab.dataset.target).style.display = 'block';
  });
});

// 自動帶今天日期
document.getElementById('priceUpdated').value = new Date().toISOString().slice(0,10).replace(/-/g, '.');

// 表單送出
document.getElementById('materialForm').addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  document.getElementById('footStatus').textContent = '儲存中…';
  try {
    const res = await fetch('/api/materials', {method: 'POST', body: fd});
    const data = await res.json();
    if (data.ok) {
      document.getElementById('footStatus').textContent = `儲存成功 · ${data.code}`;
      setTimeout(() => window.location.href = '/', 600);
    } else {
      alert('儲存失敗');
      document.getElementById('footStatus').textContent = '儲存失敗';
    }
  } catch (err) {
    alert('錯誤:' + err.message);
  }
});

// 啟動
loadCategorySelect();
document.getElementById('footStatus').textContent = '準備就緒';
