"""
漣一設計 ｜ 材料庫
本地端 Flask 應用程式
"""

import os
import sys
import sqlite3
import shutil
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory, abort

# ─────────────────────────────────────────────────────
# 路徑設定 — 確保打包成 .exe 後也能找到正確的資料夾
# ─────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent

DATA_DIR = BASE_DIR / 'data'
PHOTO_DIR = DATA_DIR / 'photos'
DB_PATH = DATA_DIR / 'lianyi.db'

DATA_DIR.mkdir(exist_ok=True)
PHOTO_DIR.mkdir(exist_ok=True)

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB 圖片上限


# ─────────────────────────────────────────────────────
# 資料庫初始化
# ─────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    # 分類表
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code_prefix TEXT NOT NULL UNIQUE,
        sort_order INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # 材料表
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        category_id INTEGER NOT NULL,
        subcategory TEXT,
        name TEXT NOT NULL,
        name_en TEXT,
        spec TEXT,
        detail TEXT,
        unit TEXT,
        price_material REAL,
        price_labor REAL,
        price_updated TEXT,
        supplier TEXT,
        supplier_contact TEXT,
        brand TEXT,
        model TEXT,
        status TEXT DEFAULT '常用',
        client_about TEXT,
        client_care TEXT,
        internal_note TEXT,
        bug_note TEXT,
        usage_locations TEXT,
        tags TEXT,
        photo_main TEXT,
        photo_subs TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )''')

    # 案場表
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        client_name TEXT,
        client_type TEXT,
        area REAL,
        area_unit TEXT DEFAULT '坪',
        completed_date TEXT,
        foreword TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    # 案場-材料關聯表
    c.execute('''CREATE TABLE IF NOT EXISTS project_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        material_id INTEGER NOT NULL,
        location TEXT,
        quantity REAL,
        note TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
        FOREIGN KEY (material_id) REFERENCES materials (id) ON DELETE CASCADE
    )''')

    # 預設分類(第一次啟動時)
    default_cats = [
        ('玻璃', 'GL', 1),
        ('板材', 'WD', 2),
        ('面材', 'VN', 3),
        ('磁磚', 'TL', 4),
        ('石材', 'ST', 5),
        ('塗料', 'PT', 6),
        ('金屬', 'MT', 7),
        ('五金', 'HW', 8),
        ('織品', 'FB', 9),
        ('燈具', 'LT', 10),
    ]
    for name, prefix, order in default_cats:
        try:
            c.execute('INSERT INTO categories (name, code_prefix, sort_order) VALUES (?, ?, ?)',
                      (name, prefix, order))
        except sqlite3.IntegrityError:
            pass  # 已存在

    conn.commit()
    conn.close()


def gen_next_code(category_id):
    """產生下一個材料編號,例如 GL-019"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT code_prefix FROM categories WHERE id = ?', (category_id,))
    prefix_row = c.fetchone()
    if not prefix_row:
        conn.close()
        return None
    prefix = prefix_row['code_prefix']

    c.execute('SELECT code FROM materials WHERE code LIKE ? ORDER BY code DESC LIMIT 1',
              (f'{prefix}-%',))
    row = c.fetchone()
    conn.close()

    if row:
        try:
            num = int(row['code'].split('-')[1]) + 1
        except (IndexError, ValueError):
            num = 1
    else:
        num = 1
    return f'{prefix}-{num:03d}'


# ─────────────────────────────────────────────────────
# 路由 — 頁面
# ─────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('admin.html')


@app.route('/new')
def material_new():
    return render_template('new.html')


@app.route('/edit/<int:mid>')
def material_edit(mid):
    return render_template('edit.html', material_id=mid)


@app.route('/material/<int:mid>')
def material_view(mid):
    return render_template('admin.html', material_id=mid)


@app.route('/projects')
def projects_page():
    return render_template('projects.html')


@app.route('/project/<int:pid>')
def project_detail(pid):
    return render_template('project_detail.html', project_id=pid)


@app.route('/book/<int:pid>')
def project_book(pid):
    """產生案場業主版材料書"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM projects WHERE id = ?', (pid,))
    project = c.fetchone()
    if not project:
        conn.close()
        return abort(404)

    # 抓出這個案場所有材料,依分類組織
    c.execute('''SELECT pm.location, pm.quantity, pm.note,
                        m.*, cat.name as cat_name, cat.sort_order as cat_order
                 FROM project_materials pm
                 JOIN materials m ON pm.material_id = m.id
                 JOIN categories cat ON m.category_id = cat.id
                 WHERE pm.project_id = ?
                 ORDER BY cat.sort_order, m.code''', (pid,))
    items = c.fetchall()
    conn.close()

    # 按分類分組
    from collections import OrderedDict
    chapters = OrderedDict()
    for it in items:
        cat = it['cat_name']
        if cat not in chapters:
            chapters[cat] = []
        chapters[cat].append(dict(it))

    return render_template('book.html',
                           project=dict(project),
                           chapters=chapters)


# ─────────────────────────────────────────────────────
# 路由 — API(資料操作)
# ─────────────────────────────────────────────────────
@app.route('/api/categories', methods=['GET'])
def api_categories():
    conn = get_db()
    cats = conn.execute('''SELECT c.*, COUNT(m.id) as count
                           FROM categories c
                           LEFT JOIN materials m ON c.id = m.category_id
                           GROUP BY c.id
                           ORDER BY c.sort_order''').fetchall()
    conn.close()
    return jsonify([dict(c) for c in cats])


@app.route('/api/categories', methods=['POST'])
def api_category_create():
    data = request.json
    conn = get_db()
    try:
        conn.execute('INSERT INTO categories (name, code_prefix, sort_order) VALUES (?, ?, ?)',
                     (data['name'], data['code_prefix'].upper(), data.get('sort_order', 99)))
        conn.commit()
        conn.close()
        return jsonify({'ok': True})
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/categories/<int:cid>', methods=['PUT'])
def api_category_update(cid):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE categories SET name = ?, code_prefix = ? WHERE id = ?',
                 (data['name'], data['code_prefix'].upper(), cid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/categories/<int:cid>', methods=['DELETE'])
def api_category_delete(cid):
    conn = get_db()
    # 檢查底下有沒有材料
    count = conn.execute('SELECT COUNT(*) as c FROM materials WHERE category_id = ?', (cid,)).fetchone()['c']
    if count > 0:
        conn.close()
        return jsonify({'ok': False, 'error': f'分類底下還有 {count} 個材料,無法刪除'}), 400
    conn.execute('DELETE FROM categories WHERE id = ?', (cid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/materials', methods=['GET'])
def api_materials():
    cat_id = request.args.get('category_id')
    q = request.args.get('q', '').strip()

    conn = get_db()
    sql = '''SELECT m.*, c.name as cat_name, c.code_prefix
             FROM materials m
             JOIN categories c ON m.category_id = c.id
             WHERE 1=1'''
    params = []
    if cat_id and cat_id != 'all':
        sql += ' AND m.category_id = ?'
        params.append(cat_id)
    if q:
        sql += ' AND (m.name LIKE ? OR m.code LIKE ? OR m.supplier LIKE ? OR m.tags LIKE ?)'
        params.extend([f'%{q}%'] * 4)
    sql += ' ORDER BY m.updated_at DESC'

    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/materials/<int:mid>', methods=['GET'])
def api_material_one(mid):
    conn = get_db()
    row = conn.execute('''SELECT m.*, c.name as cat_name
                          FROM materials m
                          JOIN categories c ON m.category_id = c.id
                          WHERE m.id = ?''', (mid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'ok': False}), 404
    return jsonify(dict(row))


@app.route('/api/materials', methods=['POST'])
def api_material_create():
    data = request.form.to_dict()
    cat_id = int(data['category_id'])
    code = gen_next_code(cat_id)

    # 處理上傳照片
    photo_main = ''
    photo_subs = []

    if 'photo_main' in request.files:
        f = request.files['photo_main']
        if f.filename:
            target_dir = PHOTO_DIR / code
            target_dir.mkdir(exist_ok=True)
            ext = Path(f.filename).suffix.lower()
            target = target_dir / f'main{ext}'
            f.save(str(target))
            photo_main = f'{code}/main{ext}'

    for i in range(1, 4):
        key = f'photo_sub_{i}'
        if key in request.files:
            f = request.files[key]
            if f.filename:
                target_dir = PHOTO_DIR / code
                target_dir.mkdir(exist_ok=True)
                ext = Path(f.filename).suffix.lower()
                target = target_dir / f'sub_{i}{ext}'
                f.save(str(target))
                photo_subs.append(f'{code}/sub_{i}{ext}')

    conn = get_db()
    conn.execute('''INSERT INTO materials
                    (code, category_id, subcategory, name, name_en, spec, detail, unit,
                     price_material, price_labor, price_updated,
                     supplier, supplier_contact, brand, model, status,
                     client_about, client_care, internal_note, bug_note,
                     usage_locations, tags, photo_main, photo_subs)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                 (code, cat_id, data.get('subcategory', ''),
                  data['name'], data.get('name_en', ''),
                  data.get('spec', ''), data.get('detail', ''),
                  data.get('unit', ''),
                  float(data['price_material']) if data.get('price_material') else None,
                  float(data['price_labor']) if data.get('price_labor') else None,
                  data.get('price_updated', ''),
                  data.get('supplier', ''), data.get('supplier_contact', ''),
                  data.get('brand', ''), data.get('model', ''),
                  data.get('status', '常用'),
                  data.get('client_about', ''), data.get('client_care', ''),
                  data.get('internal_note', ''), data.get('bug_note', ''),
                  data.get('usage_locations', ''), data.get('tags', ''),
                  photo_main, ','.join(photo_subs)))
    conn.commit()
    conn.close()

    return jsonify({'ok': True, 'code': code})


@app.route('/api/materials/<int:mid>', methods=['PUT'])
def api_material_update(mid):
    """編輯材料 — 接受 form-data,可同時更新欄位和照片"""
    data = request.form.to_dict()
    conn = get_db()
    c = conn.cursor()

    # 取現有材料(為了拿到 code,照片路徑要用)
    existing = c.execute('SELECT * FROM materials WHERE id = ?', (mid,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({'ok': False, 'error': 'not found'}), 404
    code = existing['code']

    # 處理照片(只在有上傳新檔案時才覆蓋)
    photo_main = existing['photo_main']
    photo_subs_list = (existing['photo_subs'] or '').split(',')
    photo_subs_list = [p for p in photo_subs_list if p]

    if 'photo_main' in request.files:
        f = request.files['photo_main']
        if f.filename:
            target_dir = PHOTO_DIR / code
            target_dir.mkdir(exist_ok=True)
            ext = Path(f.filename).suffix.lower()
            target = target_dir / f'main{ext}'
            f.save(str(target))
            photo_main = f'{code}/main{ext}'

    # 副圖:用 photo_sub_1, 2, 3 表示要更新某張
    for i in range(1, 4):
        key = f'photo_sub_{i}'
        if key in request.files:
            f = request.files[key]
            if f.filename:
                target_dir = PHOTO_DIR / code
                target_dir.mkdir(exist_ok=True)
                ext = Path(f.filename).suffix.lower()
                target = target_dir / f'sub_{i}{ext}'
                f.save(str(target))
                new_path = f'{code}/sub_{i}{ext}'
                # 取代或新增
                replaced = False
                for idx, existing_path in enumerate(photo_subs_list):
                    if f'/sub_{i}' in existing_path:
                        photo_subs_list[idx] = new_path
                        replaced = True
                        break
                if not replaced:
                    photo_subs_list.append(new_path)

    # 處理刪除照片(前端可送 remove_photo_main=1, remove_photo_sub_1=1...)
    if data.get('remove_photo_main') == '1':
        if photo_main:
            try:
                (PHOTO_DIR / photo_main).unlink(missing_ok=True)
            except Exception:
                pass
        photo_main = ''

    for i in range(1, 4):
        if data.get(f'remove_photo_sub_{i}') == '1':
            new_list = []
            for p in photo_subs_list:
                if f'/sub_{i}' in p:
                    try:
                        (PHOTO_DIR / p).unlink(missing_ok=True)
                    except Exception:
                        pass
                else:
                    new_list.append(p)
            photo_subs_list = new_list

    c.execute('''UPDATE materials SET
                    category_id = ?, subcategory = ?,
                    name = ?, name_en = ?,
                    spec = ?, detail = ?, unit = ?,
                    price_material = ?, price_labor = ?, price_updated = ?,
                    supplier = ?, supplier_contact = ?,
                    brand = ?, model = ?, status = ?,
                    client_about = ?, client_care = ?,
                    internal_note = ?, bug_note = ?,
                    usage_locations = ?, tags = ?,
                    photo_main = ?, photo_subs = ?,
                    updated_at = CURRENT_TIMESTAMP
                 WHERE id = ?''',
              (int(data.get('category_id', existing['category_id'])),
               data.get('subcategory', ''),
               data.get('name', existing['name']),
               data.get('name_en', ''),
               data.get('spec', ''), data.get('detail', ''),
               data.get('unit', existing['unit']),
               float(data['price_material']) if data.get('price_material') else None,
               float(data['price_labor']) if data.get('price_labor') else None,
               data.get('price_updated', ''),
               data.get('supplier', ''), data.get('supplier_contact', ''),
               data.get('brand', ''), data.get('model', ''),
               data.get('status', '常用'),
               data.get('client_about', ''), data.get('client_care', ''),
               data.get('internal_note', ''), data.get('bug_note', ''),
               data.get('usage_locations', ''), data.get('tags', ''),
               photo_main, ','.join(photo_subs_list),
               mid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'code': code})


@app.route('/api/materials/<int:mid>', methods=['DELETE'])
def api_material_delete(mid):
    """刪除材料 — 連同照片資料夾一起刪"""
    conn = get_db()
    row = conn.execute('SELECT code FROM materials WHERE id = ?', (mid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'ok': False, 'error': 'not found'}), 404

    code = row['code']
    conn.execute('DELETE FROM materials WHERE id = ?', (mid,))
    conn.commit()
    conn.close()

    # 刪掉照片資料夾
    photo_folder = PHOTO_DIR / code
    if photo_folder.exists():
        try:
            shutil.rmtree(str(photo_folder))
        except Exception:
            pass

    return jsonify({'ok': True})


@app.route('/api/materials/<int:mid>/duplicate', methods=['POST'])
def api_material_duplicate(mid):
    """複製材料 — 產生新編號,所有欄位帶過去,照片也複製一份"""
    conn = get_db()
    c = conn.cursor()
    src = c.execute('SELECT * FROM materials WHERE id = ?', (mid,)).fetchone()
    if not src:
        conn.close()
        return jsonify({'ok': False, 'error': 'not found'}), 404

    new_code = gen_next_code(src['category_id'])

    # 複製照片資料夾
    src_dir = PHOTO_DIR / src['code']
    dst_dir = PHOTO_DIR / new_code
    new_photo_main = ''
    new_photo_subs = ''

    if src_dir.exists():
        try:
            shutil.copytree(str(src_dir), str(dst_dir))
            if src['photo_main']:
                new_photo_main = src['photo_main'].replace(src['code'], new_code, 1)
            if src['photo_subs']:
                new_photo_subs = ','.join(
                    p.replace(src['code'], new_code, 1)
                    for p in src['photo_subs'].split(',') if p
                )
        except Exception:
            pass

    c.execute('''INSERT INTO materials
                 (code, category_id, subcategory, name, name_en, spec, detail, unit,
                  price_material, price_labor, price_updated,
                  supplier, supplier_contact, brand, model, status,
                  client_about, client_care, internal_note, bug_note,
                  usage_locations, tags, photo_main, photo_subs)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
              (new_code, src['category_id'], src['subcategory'],
               src['name'] + ' (副本)', src['name_en'],
               src['spec'], src['detail'], src['unit'],
               src['price_material'], src['price_labor'], src['price_updated'],
               src['supplier'], src['supplier_contact'],
               src['brand'], src['model'], src['status'],
               src['client_about'], src['client_care'],
               src['internal_note'], src['bug_note'],
               src['usage_locations'], src['tags'],
               new_photo_main, new_photo_subs))

    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'id': new_id, 'code': new_code})


@app.route('/api/next-code/<int:cat_id>')
def api_next_code(cat_id):
    return jsonify({'code': gen_next_code(cat_id)})


@app.route('/api/projects', methods=['GET'])
def api_projects():
    conn = get_db()
    rows = conn.execute('''SELECT p.*,
                                  (SELECT COUNT(*) FROM project_materials pm WHERE pm.project_id = p.id) as material_count
                           FROM projects p
                           ORDER BY p.completed_date DESC, p.id DESC''').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/projects/<int:pid>', methods=['GET'])
def api_project_one(pid):
    conn = get_db()
    row = conn.execute('SELECT * FROM projects WHERE id = ?', (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'ok': False}), 404
    project = dict(row)

    # 抓這個案場用了哪些材料
    items = conn.execute('''SELECT pm.id as pm_id, pm.material_id, pm.location, pm.quantity, pm.note,
                                   m.code, m.name, m.unit, m.price_material, m.photo_main,
                                   c.name as cat_name
                            FROM project_materials pm
                            JOIN materials m ON pm.material_id = m.id
                            JOIN categories c ON m.category_id = c.id
                            WHERE pm.project_id = ?
                            ORDER BY c.sort_order, m.code''', (pid,)).fetchall()
    project['materials'] = [dict(it) for it in items]
    conn.close()
    return jsonify(project)


@app.route('/api/projects', methods=['POST'])
def api_project_create():
    data = request.json
    conn = get_db()
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO projects (code, name, client_name, client_type, area, area_unit,
                                            completed_date, foreword)
                     VALUES (?,?,?,?,?,?,?,?)''',
                  (data['code'], data['name'],
                   data.get('client_name', ''), data.get('client_type', ''),
                   float(data['area']) if data.get('area') else None,
                   data.get('area_unit', '坪'),
                   data.get('completed_date', ''),
                   data.get('foreword', '')))
        pid = c.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'ok': True, 'id': pid})
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/projects/<int:pid>', methods=['PUT'])
def api_project_update(pid):
    data = request.json
    conn = get_db()
    conn.execute('''UPDATE projects SET
                        code = ?, name = ?, client_name = ?, client_type = ?,
                        area = ?, area_unit = ?, completed_date = ?, foreword = ?
                    WHERE id = ?''',
                 (data['code'], data['name'],
                  data.get('client_name', ''), data.get('client_type', ''),
                  float(data['area']) if data.get('area') else None,
                  data.get('area_unit', '坪'),
                  data.get('completed_date', ''),
                  data.get('foreword', ''),
                  pid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/projects/<int:pid>', methods=['DELETE'])
def api_project_delete(pid):
    conn = get_db()
    conn.execute('DELETE FROM projects WHERE id = ?', (pid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/projects/<int:pid>/materials', methods=['POST'])
def api_project_add_material(pid):
    """加一筆材料到案場"""
    data = request.json
    conn = get_db()
    conn.execute('''INSERT INTO project_materials (project_id, material_id, location, quantity, note)
                    VALUES (?,?,?,?,?)''',
                 (pid, int(data['material_id']),
                  data.get('location', ''),
                  float(data['quantity']) if data.get('quantity') else None,
                  data.get('note', '')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/project-materials/<int:pmid>', methods=['PUT'])
def api_project_material_update(pmid):
    """更新案場-材料關聯(改位置、數量、備註)"""
    data = request.json
    conn = get_db()
    conn.execute('''UPDATE project_materials SET location = ?, quantity = ?, note = ?
                    WHERE id = ?''',
                 (data.get('location', ''),
                  float(data['quantity']) if data.get('quantity') else None,
                  data.get('note', ''),
                  pmid))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/project-materials/<int:pmid>', methods=['DELETE'])
def api_project_material_remove(pmid):
    """從案場移除某筆材料"""
    conn = get_db()
    conn.execute('DELETE FROM project_materials WHERE id = ?', (pmid,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/photos/<path:filename>')
def photo_serve(filename):
    return send_from_directory(str(PHOTO_DIR), filename)


# ─────────────────────────────────────────────────────
# 啟動
# ─────────────────────────────────────────────────────
def open_browser():
    """延遲打開瀏覽器,等 server 啟動"""
    time.sleep(1.2)
    webbrowser.open('http://127.0.0.1:5005')


if __name__ == '__main__':
    init_db()
    print('━' * 60)
    print('  漣一設計 ｜ 材料庫')
    print('━' * 60)
    print(f'  資料位置:{DATA_DIR}')
    print(f'  網址:http://127.0.0.1:5005')
    print('  關閉這個視窗即可結束程式')
    print('━' * 60)
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host='127.0.0.1', port=5005, debug=False)
