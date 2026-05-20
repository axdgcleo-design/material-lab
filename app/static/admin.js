// ━━━━━━━━━━ 漣一設計 ｜ 材料庫管理介面 ━━━━━━━━━━

let currentCategoryId = 'all';
let currentCategoryName = '材 料 庫';
let currentSearch = '';

// 載入分類
async function loadCategories() {
  const res = await fetch('/api/categories');
  const cats = await res.json();

  let total = 0;
  cats.forEach(c => total += c.count);
  document.getElementById('statTotal').textContent = total;
  document.getElementById('statUpdated').textContent = new Date().toISOString().slice(0,7).replace('-','.');

  const nav = document.getElementById('navCategories');
  let html = `
    <div class="nav-item ${currentCategoryId === 'all' ? 'active' : ''}" data-id="all" data-name="材 料 庫">
      <span class="nav-item-name">全部</span>
      <span class="nav-count">${total}</span>
    </div>
  `;
  cats.forEach(c => {
    html += `
      <div class="nav-item ${currentCategoryId == c.id ? 'active' : ''}" data-id="${c.id}" data-name="${c.name}">
        <span class="nav-item-name">${c.name}</span>
        <span class="nav-count">${c.count}</span>
        <div class="nav-actions">
          <button class="nav-action-btn" onclick="renameCategory(event, ${c.id}, '${c.name}', '${c.code_prefix}')" title="重新命名">✎</button>
          <button class="nav-action-btn delete" onclick="deleteCategory(event, ${c.id}, '${c.name}', ${c.count})" title="刪除">×</button>
        </div>
      </div>
    `;
  });
  nav.innerHTML = html;

  // 綁定切換分類
  nav.querySelectorAll('.nav-item').forEach(el => {
    el.addEventListener('click', e => {
      if (e.target.closest('.nav-action-btn')) return;
      currentCategoryId = el.dataset.id;
      currentCategoryName = el.dataset.name;
      document.getElementById('mainTitle').textContent = currentCategoryName;
      loadCategories();
      loadMaterials();
    });
  });
}

// 載入材料卡片
async function loadMaterials() {
  const params = new URLSearchParams();
  if (currentCategoryId !== 'all') params.set('category_id', currentCategoryId);
  if (currentSearch) params.set('q', currentSearch);

  const res = await fetch('/api/materials?' + params);
  const items = await res.json();
  const gallery = document.getElementById('gallery');

  if (items.length === 0) {
    gallery.innerHTML = `
      <div class="empty-state">
        <div class="empty-title">${currentSearch ? '沒有符合的材料' : '這個分類還是空的'}</div>
        <div class="empty-sub">${currentSearch ? '試試別的關鍵字' : '點右上方「+ 新增材料」開始累積你的第一筆。'}</div>
      </div>
    `;
    return;
  }

  let html = '';
  items.forEach(m => {
    html += `
      <div class="card" data-id="${m.id}">
        <div class="card-img">
          ${m.photo_main ? `<img src="/photos/${m.photo_main}" />` : `<span class="placeholder">No image</span>`}
          <div class="card-code">${m.code}</div>
        </div>
        <div class="card-body">
          <div class="card-name">${m.name}</div>
          <div class="card-spec">${[m.spec, m.detail, m.supplier].filter(Boolean).join(' · ') || '—'}</div>
          <div class="card-meta">
            <div class="card-price">${m.price_material ? Number(m.price_material).toLocaleString() : '—'}<span class="unit">${m.unit ? '/' + m.unit : ''}</span></div>
          </div>
        </div>
      </div>
    `;
  });
  gallery.innerHTML = html;

  // 綁定點擊
  gallery.querySelectorAll('.card').forEach(el => {
    el.addEventListener('click', () => {
      gallery.querySelectorAll('.card').forEach(c => c.classList.remove('selected'));
      el.classList.add('selected');
      showDetail(el.dataset.id);
    });
  });
}

// 顯示右側細節
async function showDetail(id) {
  const res = await fetch('/api/materials/' + id);
  const m = await res.json();
  const detail = document.getElementById('detail');

  let html = `
    <div class="detail-head">
      <div class="detail-code">${m.code} ｜ ${m.cat_name}</div>
      <div class="detail-name">${m.name}</div>
      ${m.name_en ? `<div class="detail-name-en">${m.name_en}</div>` : ''}
    </div>
    <div class="detail-hero">
      ${m.photo_main ? `<img src="/photos/${m.photo_main}" />` : ''}
    </div>
    <div class="spec-row"><div class="spec-label">CATEGORY</div><div class="spec-val">${m.cat_name}${m.subcategory ? ' / ' + m.subcategory : ''}</div></div>
    ${m.spec ? `<div class="spec-row"><div class="spec-label">SPEC</div><div class="spec-val">${m.spec}${m.detail ? ' · ' + m.detail : ''}</div></div>` : ''}
    ${m.price_material ? `<div class="spec-row"><div class="spec-label">PRICE</div><div class="spec-val"><span class="accent">${Number(m.price_material).toLocaleString()}</span> 元 / ${m.unit || ''}</div></div>` : ''}
    ${m.supplier ? `<div class="spec-row"><div class="spec-label">SUPPLIER</div><div class="spec-val">${m.supplier}${m.supplier_contact ? ' · ' + m.supplier_contact : ''}</div></div>` : ''}
    ${m.brand ? `<div class="spec-row"><div class="spec-label">BRAND</div><div class="spec-val">${m.brand}${m.model ? ' / ' + m.model : ''}</div></div>` : ''}
  `;

  if (m.client_about) {
    html += `<div class="section-title">業主版說明</div><div class="note-block client">${m.client_about}</div>`;
  }
  if (m.client_care) {
    html += `<div class="section-title">業主版保養</div><div class="note-block client">${m.client_care}</div>`;
  }
  if (m.internal_note) {
    html += `<div class="section-title">施工注意</div><div class="alert-block">${m.internal_note}</div>`;
  }
  if (m.bug_note) {
    html += `<div class="section-title">踩雷筆記</div><div class="alert-block">${m.bug_note}</div>`;
  }

  // 動作列
  html += `
    <div class="detail-actions">
      <a class="btn" href="/edit/${m.id}">✎ 編輯</a>
      <button class="btn btn-ghost" onclick="duplicateMaterial(${m.id})">⎘ 複製</button>
      <button class="btn btn-ghost danger-btn" onclick="deleteMaterial(${m.id}, '${m.name.replace(/'/g, "\\'")}', '${m.code}')">🗑 刪除</button>
    </div>
  `;

  detail.innerHTML = html;
}

// 複製材料
async function duplicateMaterial(id) {
  if (!confirm('複製這筆材料?系統會用同樣的內容建立一筆新的(新編號 + 名字加「(副本)」),你可以再去編輯。')) return;
  const res = await fetch('/api/materials/' + id + '/duplicate', {method: 'POST'});
  const data = await res.json();
  if (data.ok) {
    // 直接跳到編輯頁,讓使用者改新副本的內容
    window.location.href = '/edit/' + data.id;
  } else {
    alert('複製失敗');
  }
}

// 刪除材料
async function deleteMaterial(id, name, code) {
  if (!confirm(`確定要刪除「${name}」(${code})?\n\n這個動作不能還原,連同照片也會一起刪除。`)) return;
  if (!confirm('再次確認:刪除後無法復原,真的要刪?')) return;
  const res = await fetch('/api/materials/' + id, {method: 'DELETE'});
  const data = await res.json();
  if (data.ok) {
    document.getElementById('detail').innerHTML = '<div class="detail-empty"><div class="empty-title">已刪除</div><div class="empty-sub">材料和照片已從系統移除。</div></div>';
    loadCategories();
    loadMaterials();
  } else {
    alert('刪除失敗:' + (data.error || ''));
  }
}

// 新增分類
document.getElementById('addCatBtn').addEventListener('click', () => {
  document.getElementById('catModal').style.display = 'flex';
  document.getElementById('newCatName').value = '';
  document.getElementById('newCatPrefix').value = '';
  document.getElementById('newCatName').focus();
});

document.getElementById('saveCatBtn').addEventListener('click', async () => {
  const name = document.getElementById('newCatName').value.trim();
  const prefix = document.getElementById('newCatPrefix').value.trim().toUpperCase();
  if (!name || !prefix) {
    alert('請填寫分類名稱與編號前綴');
    return;
  }
  const res = await fetch('/api/categories', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name, code_prefix: prefix})
  });
  const data = await res.json();
  if (data.ok) {
    document.getElementById('catModal').style.display = 'none';
    loadCategories();
  } else {
    alert('新增失敗:' + (data.error || '未知錯誤'));
  }
});

// 重新命名分類
async function renameCategory(e, id, name, prefix) {
  e.stopPropagation();
  const newName = prompt(`重新命名「${name}」為:`, name);
  if (!newName || newName === name) return;
  const newPrefix = prompt(`編號前綴(現為 ${prefix},改名不影響已存在的編號):`, prefix);
  if (!newPrefix) return;
  const res = await fetch('/api/categories/' + id, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: newName, code_prefix: newPrefix.toUpperCase()})
  });
  const data = await res.json();
  if (data.ok) loadCategories();
  else alert('更新失敗');
}

// 刪除分類
async function deleteCategory(e, id, name, count) {
  e.stopPropagation();
  if (count > 0) {
    alert(`「${name}」底下還有 ${count} 個材料,請先移到其他分類再刪除。`);
    return;
  }
  if (!confirm(`確認刪除分類「${name}」?`)) return;
  const res = await fetch('/api/categories/' + id, {method: 'DELETE'});
  const data = await res.json();
  if (data.ok) loadCategories();
  else alert('刪除失敗:' + data.error);
}

// 搜尋
let searchTimer;
document.getElementById('searchInput').addEventListener('input', e => {
  currentSearch = e.target.value.trim();
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadMaterials(), 250);
});

// 初始化
loadCategories();
loadMaterials();
