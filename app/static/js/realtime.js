/* Real-time sync — included in all main pages */
(function () {
    'use strict';

    const path = window.location.pathname;
    const socket = io({ transports: ['websocket', 'polling'] });

    // ── Live indicator ──────────────────────────────────────────
    function setLiveStatus(connected) {
        const dot = document.getElementById('live-dot');
        const lbl = document.getElementById('live-label');
        if (!dot) return;
        dot.style.background = connected ? '#10b981' : '#ef4444';
        if (lbl) lbl.textContent = connected ? 'LIVE' : 'OFF';
    }

    socket.on('connect',    () => setLiveStatus(true));
    socket.on('disconnect', () => setLiveStatus(false));

    // ── Toast ────────────────────────────────────────────────────
    function showToast(msg, type) {
        const colors = { success: '#10b981', warning: '#f59e0b', info: '#3b82f6' };
        const icons  = { success: '✓', warning: '⚠', info: 'ℹ' };
        const color  = colors[type] || colors.info;
        const icon   = icons[type]  || icons.info;

        const t = document.createElement('div');
        t.style.cssText = [
            'position:fixed;bottom:24px;right:24px;z-index:99999',
            'background:rgba(22,22,38,0.97)',
            'border:1px solid rgba(255,255,255,0.12)',
            'color:#fff;padding:14px 18px;border-radius:12px',
            'display:flex;align-items:center;gap:12px',
            'font-size:0.88rem;max-width:360px',
            'box-shadow:0 8px 32px rgba(0,0,0,0.45)',
            'animation:rt-slide-in 0.3s ease'
        ].join(';');
        t.innerHTML = `
            <span style="font-size:1.1rem;color:${color};flex-shrink:0">${icon}</span>
            <span style="flex:1;line-height:1.4">${msg}</span>
            <button onclick="this.parentElement.remove()"
                    style="background:none;border:none;color:#888;cursor:pointer;font-size:1rem;padding:0 0 0 6px">✕</button>`;
        document.body.appendChild(t);
        setTimeout(() => { if (t.parentElement) t.remove(); }, 6000);
    }

    // ── Auto-reload with debounce ───────────────────────────────
    let reloadTimer = null;
    function scheduleReload(ms) {
        clearTimeout(reloadTimer);
        reloadTimer = setTimeout(() => window.location.reload(), ms || 1800);
    }

    // Pages that should auto-reload on each event type
    const ON_INVENTORY = ['/inventory_list', '/dashboard', '/reports', '/notifications', '/sales'];
    const ON_BORROW    = ['/inventory_list', '/borrowed_items', '/borrow_list', '/dashboard', '/reports'];
    const ON_SALE      = ['/sales', '/dashboard', '/reports', '/inventory_list', '/pos/transactions'];

    function matchesPath(list) {
        return list.some(p => path === p || path.startsWith(p + '?'));
    }

    // ── POS live stock update (no reload needed) ────────────────
    function updatePosCards(updates) {
        if (!updates || !updates.length) return;
        updates.forEach(function (u) {
            const card = document.querySelector('.prod-card[data-id="' + u.id + '"]');
            if (!card) return;

            card.dataset.balance = u.qty;
            const stockEl = card.querySelector('.prod-stock');
            const btn     = card.querySelector('.prod-add-btn');

            if (u.qty <= 0) {
                card.classList.add('out-of-stock');
                if (stockEl) { stockEl.className = 'prod-stock out'; stockEl.textContent = 'Out of stock'; }
                if (btn) btn.disabled = true;
            } else {
                card.classList.remove('out-of-stock');
                const reorder = parseInt(u.reorder || 5);
                if (stockEl) {
                    stockEl.className = 'prod-stock' + (u.qty <= reorder ? ' low' : '');
                    stockEl.textContent = 'Stock: ' + u.qty;
                }
                if (btn) btn.disabled = false;
            }

            // Keep cart in sync
            if (window.cart && window.cart[u.id]) {
                window.cart[u.id].balance = u.qty;
            }
        });
    }

    // ── Event handlers ─────────────────────────────────────────
    socket.on('inventory_change', function (data) {
        const by  = data.user  || 'another user';
        const act = data.action || 'updated';

        if (path.startsWith('/pos') && !path.startsWith('/pos/transactions')) {
            updatePosCards(data.updates);
            showToast('Stock updated by ' + by, 'info');
            return;
        }

        showToast('Inventory ' + act + ' by ' + by, 'info');
        if (matchesPath(ON_INVENTORY)) scheduleReload();
    });

    socket.on('borrow_change', function (data) {
        const by  = data.user   || 'another user';
        const act = data.action || 'updated';

        if (path.startsWith('/pos') && !path.startsWith('/pos/transactions')) {
            updatePosCards(data.updates);
            showToast('Borrow ' + act + ' by ' + by, 'info');
            return;
        }

        showToast('Borrowing ' + act + ' by ' + by, 'info');
        if (matchesPath(ON_BORROW)) scheduleReload();
    });

    socket.on('sale_made', function (data) {
        const receipt = data.receipt_no || '';
        const total   = parseFloat(data.total || 0).toFixed(2);

        if (path.startsWith('/pos') && !path.startsWith('/pos/transactions')) {
            updatePosCards(data.updates);
            showToast('Sale completed: ' + receipt + ' — ₱' + total, 'success');
            return;
        }

        showToast('New sale: ' + receipt + ' — ₱' + total, 'success');
        if (matchesPath(ON_SALE)) scheduleReload();
    });

    // ── Inject live indicator into sidebar ─────────────────────
    // Runs after DOM is ready
    function injectLiveBadge() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar || document.getElementById('live-dot')) return;

        const badge = document.createElement('div');
        badge.id = 'live-badge';
        badge.style.cssText = [
            'position:absolute;bottom:18px;left:50%;transform:translateX(-50%)',
            'display:flex;align-items:center;gap:6px',
            'font-size:0.65rem;font-weight:700;letter-spacing:1.5px;color:#94a3b8'
        ].join(';');
        badge.innerHTML =
            '<span id="live-dot" style="width:8px;height:8px;border-radius:50%;' +
            'background:#ef4444;display:inline-block;flex-shrink:0"></span>' +
            '<span id="live-label">OFF</span>';

        sidebar.style.position = 'relative';
        sidebar.appendChild(badge);
        setLiveStatus(socket.connected);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectLiveBadge);
    } else {
        injectLiveBadge();
    }

    // ── CSS animation keyframes ─────────────────────────────────
    const style = document.createElement('style');
    style.textContent = '@keyframes rt-slide-in{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(style);
})();
