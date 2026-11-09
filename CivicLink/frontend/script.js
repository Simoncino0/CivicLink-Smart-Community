/* =============================================
   CivicLink Dashboard - Script
   FileReader API, no server, no fetch
   ============================================= */

let appData = null;

document.addEventListener('DOMContentLoaded', () => {
    initNav();
    initFileUpload();
    initMobile();
    initSearch();
    bindFilters();
});

/* ===== Navigation ===== */
function initNav() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            const section = item.dataset.section;
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            showSection(section);
            document.getElementById('sidebar').classList.remove('open');
        });
    });
}

function showSection(name) {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById('welcomeSection').style.display = 'none';
    const el = document.getElementById(name + 'Section');
    if (el) el.style.display = 'block';

    const titles = {
        dashboard: 'Dashboard',
        segnalazioni: 'Segnalazioni del Territorio',
        oggetti: 'Oggetti Smarriti e Ritrovati',
        statistiche: 'Statistiche Dettagliate',
        info: 'Informazioni'
    };
    const subtitles = {
        dashboard: 'Panoramica della comunità',
        segnalazioni: 'Gestione delle segnalazioni territoriali',
        oggetti: 'Oggetti smarriti e ritrovati',
        statistiche: 'Analisi dei dati raccolti',
        info: 'Informazioni sul progetto'
    };
    document.getElementById('pageTitle').textContent = titles[name] || 'Dashboard';
    document.getElementById('pageSubtitle').textContent = subtitles[name] || '';

    if (appData) renderSection(name);
}

/* ===== Mobile ===== */
function initMobile() {
    const toggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
        if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

/* ===== Search ===== */
function initSearch() {
    const searchSeg = document.getElementById('searchSegnalazioni');
    const searchOg = document.getElementById('searchOggetti');
    if (searchSeg) {
        searchSeg.addEventListener('input', () => {
            if (appData) renderSegnalazioni();
        });
    }
    if (searchOg) {
        searchOg.addEventListener('input', () => {
            if (appData) renderOggetti();
        });
    }
}

/* ===== File Upload ===== */
function initFileUpload() {
    const input = document.getElementById('fileInput');
    const btn = document.getElementById('loadDataBtn');
    btn.addEventListener('click', () => input.click());

    input.addEventListener('change', e => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = ev => {
            try {
                const data = JSON.parse(ev.target.result);
                processData(data);
            } catch (err) {
                showToast('Errore: file JSON non valido. ' + err.message, 'error');
            }
        };
        reader.onerror = () => showToast('Errore nella lettura del file.', 'error');
        reader.readAsText(file);
    });
}

function processData(data) {
    if (!data.segnalazioni || !data.oggetti || !data.statistiche) {
        showToast('Il file non ha la struttura corretta di CivicLink.', 'error');
        return;
    }
    if (!Array.isArray(data.segnalazioni) || !Array.isArray(data.oggetti)) {
        showToast('Dati non validi: segnalazioni e oggetti devono essere array.', 'error');
        return;
    }
    appData = data;
    document.getElementById('welcomeSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';

    // Reset di ricerca e filtri ad ogni nuovo caricamento
    const searchSeg = document.getElementById('searchSegnalazioni');
    const searchOg = document.getElementById('searchOggetti');
    if (searchSeg) searchSeg.value = '';
    if (searchOg) searchOg.value = '';
    document.querySelectorAll('.filter-select').forEach(sel => { sel.value = ''; });

    renderAll();
    updateDataStatus(true);
    showToast('Dati caricati con successo! ' + data.segnalazioni.length + ' segnalazioni, ' + data.oggetti.length + ' oggetti.', 'success');
}

function updateDataStatus(loaded) {
    const status = document.getElementById('dataStatus');
    const text = document.getElementById('dataStatusText');
    const dot = document.getElementById('statusDot');
    const dotText = document.getElementById('statusText');
    if (loaded) {
        status.classList.add('loaded');
        text.textContent = 'Dati caricati';
        dot.classList.add('loaded');
        dotText.textContent = 'Dati connessi';
    } else {
        status.classList.remove('loaded');
        text.textContent = 'In attesa';
        dot.classList.remove('loaded');
        dotText.textContent = 'Nessun dato caricato';
    }
}

/* ===== Render ===== */
function renderAll() {
    if (!appData) return;
    renderMetrics();
    renderNavCounters();
    renderBarChart();
    renderDonuts();
    renderRecent();
    renderSegnalazioni();
    renderOggetti();
    renderStatistiche();
    populateAllFilters();
}

function renderSection(name) {
    if (name === 'dashboard') { renderMetrics(); renderBarChart(); renderDonuts(); renderRecent(); }
    if (name === 'segnalazioni') renderSegnalazioni();
    if (name === 'oggetti') renderOggetti();
    if (name === 'statistiche') renderStatistiche();
}

/* ===== Metrics ===== */
function renderMetrics() {
    const s = appData.statistiche;
    document.getElementById('statTotale').textContent = s.totale_segnalazioni || 0;
    document.getElementById('statAperte').textContent = s.segnalazioni_aperte || 0;
    document.getElementById('statLavorazione').textContent = s.segnalazioni_in_lavorazione || 0;
    document.getElementById('statRisolte').textContent = s.segnalazioni_risolte || 0;
}

function renderNavCounters() {
    document.getElementById('navCounterSeg').textContent = appData.segnalazioni.length;
    document.getElementById('navCounterOg').textContent = appData.oggetti.length;
}

/* ===== Bar Chart ===== */
function renderBarChart() {
    const container = document.getElementById('barChart');
    const labels = document.getElementById('barLabels');
    container.innerHTML = '';
    labels.innerHTML = '';

    const cats = {};
    appData.segnalazioni.forEach(s => { cats[s.categoria || 'Altro'] = (cats[s.categoria || 'Altro'] || 0) + 1; });
    const entries = Object.entries(cats).sort((a, b) => b[1] - a[1]);
    const max = Math.max(...entries.map(e => e[1]), 1);

    /* Palette dei PDF (stessi valori delle variabili CSS in :root) */
    const colors = ['#2563EB', '#16A34A', '#7C3AED', '#D97706', '#DC2626', '#8A93A8'];

    entries.forEach(([label, value], i) => {
        const col = document.createElement('div');
        col.className = 'bar-col';
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.height = '0px';
        bar.style.background = colors[i % colors.length];
        bar.title = label + ': ' + value;
        col.appendChild(bar);
        container.appendChild(col);

        const lbl = document.createElement('span');
        lbl.textContent = label;
        labels.appendChild(lbl);

        setTimeout(() => { bar.style.height = Math.max((value / max) * 170, 6) + 'px'; }, 50 + i * 60);
    });

    if (!entries.length) {
        container.innerHTML = '<p class="no-data">Nessun dato</p>';
        labels.innerHTML = '';
    }
}

/* ===== Donuts ===== */
function renderDonuts() {
    const s = appData.statistiche;
    const tot = s.totale_segnalazioni || 1;

    drawDonut('donutStato', [
        { value: s.segnalazioni_aperte || 0, color: '#D97706' },
        { value: s.segnalazioni_in_lavorazione || 0, color: '#7C3AED' },
        { value: s.segnalazioni_risolte || 0, color: '#16A34A' }
    ]);
    document.getElementById('donutStatoPct').textContent = Math.round(((s.segnalazioni_risolte || 0) / tot) * 100) + '%';

    const totOg = s.totale_oggetti || 1;
    drawDonut('donutOggetti', [
        { value: s.oggetti_smarriti || 0, color: '#D97706' },
        { value: s.oggetti_ritrovati || 0, color: '#16A34A' }
    ]);
    document.getElementById('donutOggettiPct').textContent = Math.round(((s.oggetti_ritrovati || 0) / totOg) * 100) + '%';
}

function drawDonut(id, segments) {
    const svg = document.getElementById(id);
    if (!svg) return;
    svg.innerHTML = '';

    const total = segments.reduce((a, b) => a + b.value, 0);
    const r = 42, cx = 60, cy = 60, stroke = 12; /* centro = metà del viewBox 120 */
    const circ = 2 * Math.PI * r;

    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    bg.setAttribute('cx', cx);
    bg.setAttribute('cy', cy);
    bg.setAttribute('r', r);
    bg.setAttribute('fill', 'none');
    bg.setAttribute('stroke', '#DCE4F0');
    bg.setAttribute('stroke-width', stroke);
    svg.appendChild(bg);

    if (total === 0) return;

    let offset = 0;
    segments.forEach(seg => {
        if (seg.value === 0) return;
        const pct = seg.value / total;
        const dash = pct * circ;
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', r);
        circle.setAttribute('fill', 'none');
        circle.setAttribute('stroke', seg.color);
        circle.setAttribute('stroke-width', stroke);
        circle.setAttribute('stroke-dasharray', dash + ' ' + (circ - dash));
        circle.setAttribute('stroke-dashoffset', -offset);
        circle.setAttribute('stroke-linecap', 'butt');
        svg.appendChild(circle);
        offset += dash;
    });
}

/* ===== Recent ===== */
function renderRecent() {
    const dots = ['dot-blue', 'dot-orange', 'dot-green', 'dot-purple'];

    const segEl = document.getElementById('recentSegnalazioni');
    segEl.innerHTML = '';
    const rec = [...appData.segnalazioni].sort((a, b) => new Date(b.data) - new Date(a.data)).slice(0, 5);
    if (!rec.length) {
        segEl.innerHTML = '<p class="no-data">Nessuna segnalazione</p>';
    } else {
        rec.forEach((s, i) => {
            segEl.innerHTML += '<div class="recent-item"><div class="recent-dot ' + dots[i % 4] + '"></div>' +
                '<div class="recent-info"><div class="recent-title">' + esc(s.titolo) + '</div>' +
                '<div class="recent-sub">' + esc(s.zona) + ' &bull; ' + fmtDate(s.data) + '</div></div></div>';
        });
    }

    const ogEl = document.getElementById('recentOggetti');
    ogEl.innerHTML = '';
    const recOg = [...appData.oggetti].sort((a, b) => new Date(b.data) - new Date(a.data)).slice(0, 5);
    if (!recOg.length) {
        ogEl.innerHTML = '<p class="no-data">Nessun oggetto</p>';
    } else {
        recOg.forEach((o, i) => {
            ogEl.innerHTML += '<div class="recent-item"><div class="recent-dot ' + dots[i % 4] + '"></div>' +
                '<div class="recent-info"><div class="recent-title">' + esc(o.nome) + '</div>' +
                '<div class="recent-sub">' + esc(o.luogo) + ' &bull; ' + fmtDate(o.data) + '</div></div></div>';
        });
    }
}

/* ===== Segnalazioni Table ===== */
function renderSegnalazioni() {
    const tbody = document.querySelector('#tabellaSegnalazioni tbody');
    tbody.innerHTML = '';

    const fc = document.getElementById('filterCategoria').value;
    const fs = document.getElementById('filterStato').value;
    const fp = document.getElementById('filterPriorita').value;
    const searchEl = document.getElementById('searchSegnalazioni');
    const q = searchEl ? searchEl.value.trim().toLowerCase() : '';

    let rows = [...appData.segnalazioni];
    if (q) {
        rows = rows.filter(s =>
            String(s.titolo || '').toLowerCase().includes(q) ||
            String(s.descrizione || '').toLowerCase().includes(q) ||
            String(s.zona || '').toLowerCase().includes(q) ||
            String(s.categoria || '').toLowerCase().includes(q)
        );
    }
    if (fc) rows = rows.filter(s => s.categoria === fc);
    if (fs) rows = rows.filter(s => s.stato === fs);
    if (fp) rows = rows.filter(s => s.priorita === fp);

    const noData = document.getElementById('noSegnalazioni');
    if (!rows.length) {
        noData.textContent = (q || fc || fs || fp)
            ? 'Nessun risultato con la ricerca o i filtri attuali.'
            : 'Nessuna segnalazione trovata.';
        noData.style.display = 'block';
        document.getElementById('tabellaSegnalazioni').style.display = 'none';
        return;
    }
    noData.style.display = 'none';
    document.getElementById('tabellaSegnalazioni').style.display = 'table';

    rows.forEach(s => {
        const bs = s.stato === 'Aperta' ? 'badge-aperta' : s.stato === 'In lavorazione' ? 'badge-lavorazione' : 'badge-risolta';
        const bp = s.priorita === 'Alta' ? 'badge-alta' : s.priorita === 'Media' ? 'badge-media' : 'badge-bassa';
        const tr = document.createElement('tr');
        tr.innerHTML = '<td><strong>#' + esc(String(s.id)) + '</strong></td><td>' + esc(s.titolo) + '</td><td>' + esc(s.categoria) +
            '</td><td>' + esc(s.zona) + '</td><td><span class="badge ' + bp + '">' + esc(s.priorita) +
            '</span></td><td>' + fmtDate(s.data) + '</td><td><span class="badge ' + bs + '">' + esc(s.stato) + '</span></td>';
        tbody.appendChild(tr);
    });
}

/* ===== Oggetti Table ===== */
function renderOggetti() {
    const tbody = document.querySelector('#tabellaOggetti tbody');
    tbody.innerHTML = '';

    const ft = document.getElementById('filterTipologia').value;
    const fa = document.getElementById('filterAnnuncio').value;
    const searchEl = document.getElementById('searchOggetti');
    const q = searchEl ? searchEl.value.trim().toLowerCase() : '';

    let rows = [...appData.oggetti];
    if (q) {
        rows = rows.filter(o =>
            String(o.nome || '').toLowerCase().includes(q) ||
            String(o.descrizione || '').toLowerCase().includes(q) ||
            String(o.luogo || '').toLowerCase().includes(q) ||
            String(o.tipologia || '').toLowerCase().includes(q)
        );
    }
    if (ft) rows = rows.filter(o => o.tipologia === ft);
    if (fa) rows = rows.filter(o => o.annuncio === fa);

    const noData = document.getElementById('noOggetti');
    if (!rows.length) {
        noData.textContent = (q || ft || fa)
            ? 'Nessun risultato con la ricerca o i filtri attuali.'
            : 'Nessun oggetto trovato.';
        noData.style.display = 'block';
        document.getElementById('tabellaOggetti').style.display = 'none';
        return;
    }
    noData.style.display = 'none';
    document.getElementById('tabellaOggetti').style.display = 'table';

    rows.forEach(o => {
        const bst = o.stato === 'Attivo' ? 'badge-attivo' : 'badge-risolta';
        const bann = o.annuncio === 'Smarrito' ? 'badge-aperta' : 'badge-risolta';
        const tr = document.createElement('tr');
        tr.innerHTML = '<td><strong>#' + esc(String(o.id)) + '</strong></td><td>' + esc(o.nome) + '</td><td>' + esc(o.tipologia) +
            '</td><td><span class="badge ' + bann + '">' + esc(o.annuncio) + '</span></td><td>' + esc(o.luogo) +
            '</td><td>' + fmtDate(o.data) + '</td><td><span class="badge ' + bst + '">' + esc(o.stato) + '</span></td>';
        tbody.appendChild(tr);
    });
}

/* ===== Statistiche ===== */
function renderStatistiche() {
    renderStatList('statsStato', [
        ['Aperte', appData.statistiche.segnalazioni_aperte || 0],
        ['In lavorazione', appData.statistiche.segnalazioni_in_lavorazione || 0],
        ['Risolte', appData.statistiche.segnalazioni_risolte || 0],
        ['Totale', appData.statistiche.totale_segnalazioni || 0]
    ]);

    const cats = {};
    appData.segnalazioni.forEach(s => { cats[s.categoria] = (cats[s.categoria] || 0) + 1; });
    renderStatList('statsCategoria', Object.entries(cats).sort((a, b) => b[1] - a[1]));

    const prio = {};
    appData.segnalazioni.forEach(s => { prio[s.priorita] = (prio[s.priorita] || 0) + 1; });
    renderStatList('statsPriorita', Object.entries(prio));

    const tip = {};
    appData.oggetti.forEach(o => { tip[o.tipologia] = (tip[o.tipologia] || 0) + 1; });
    const tipArr = Object.entries(tip).sort((a, b) => b[1] - a[1]);
    tipArr.push(['Smarriti', appData.statistiche.oggetti_smarriti || 0]);
    tipArr.push(['Ritrovati', appData.statistiche.oggetti_ritrovati || 0]);
    renderStatList('statsTipologia', tipArr);
}

function renderStatList(id, rows) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = '';
    if (!rows.length) {
        el.innerHTML = '<p class="no-data">Nessun dato</p>';
        return;
    }
    rows.forEach(([label, value]) => {
        el.innerHTML += '<div class="stat-row"><span class="stat-row-label">' + esc(String(label)) +
            '</span><span class="stat-row-value">' + esc(String(value)) + '</span></div>';
    });
}

/* ===== Filters ===== */
function bindFilters() {
    /* Listener aggiunti UNA sola volta all'avvio, per evitare duplicati ad ogni caricamento */
    document.querySelectorAll('.filter-select').forEach(sel => {
        sel.addEventListener('change', () => {
            if (!appData) return;
            renderSegnalazioni();
            renderOggetti();
        });
    });
}

function populateAllFilters() {
    populateFilter('filterCategoria', [...new Set(appData.segnalazioni.map(s => s.categoria))]);
    populateFilter('filterStato', [...new Set(appData.segnalazioni.map(s => s.stato))]);
    populateFilter('filterPriorita', [...new Set(appData.segnalazioni.map(s => s.priorita))]);
    populateFilter('filterTipologia', [...new Set(appData.oggetti.map(o => o.tipologia))]);
    populateFilter('filterAnnuncio', [...new Set(appData.oggetti.map(o => o.annuncio))]);
}

function populateFilter(id, values) {
    const sel = document.getElementById(id);
    if (!sel) return;
    const first = sel.options[0].outerHTML;
    sel.innerHTML = first;
    values.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        sel.appendChild(opt);
    });
}

/* ===== Toast ===== */
function showToast(msg, type) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = 'toast ' + type + ' show';
    setTimeout(() => { toast.classList.remove('show'); }, 4000);
}

/* ===== Utilities ===== */
function esc(text) {
    if (text === null || text === undefined) return '';
    const d = document.createElement('div');
    d.textContent = String(text);
    return d.innerHTML;
}

function fmtDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch (e) {
        return dateStr;
    }
}