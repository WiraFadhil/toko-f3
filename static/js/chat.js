(function () {
    'use strict';

    function ready(fn) {
        if (document.readyState !== 'loading') { fn(); }
        else { document.addEventListener('DOMContentLoaded', fn); }
    }

    ready(function () {
        var launcher = document.getElementById('chatLauncher');
        var panel = document.getElementById('chatPanel');
        var closeBtn = document.getElementById('chatClose');
        var body = document.getElementById('chatBody');
        var form = document.getElementById('chatForm');
        var input = document.getElementById('chatInput');

        if (!launcher || !panel || !body) { return; }

        function scrollBottom() {
            body.scrollTop = body.scrollHeight;
        }

        function openChat() {
            panel.hidden = false;
            launcher.hidden = true;
            scrollBottom();
            if (input) { input.focus(); }
        }

        function closeChat() {
            panel.hidden = true;
            launcher.hidden = false;
        }

        function escHtml(t) {
            var div = document.createElement('div');
            div.textContent = t;
            return div.innerHTML;
        }

        function renderInline(t) {
            var h = escHtml(t);
            h = h.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            h = h.replace(/(^|[^A-Za-z0-9])\*([^*\n]+)\*/g, '$1<em>$2</em>');
            return h;
        }

        function formatBotText(text) {
            var html = '';
            var lines = (text || '').split(/\r?\n/);
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                if (!line) { continue; }
                var m = line.match(/^([-*•])\s+(.*)$/);
                if (m) {
                    html += '<div class="chat-li">' + renderInline(m[2]) + '</div>';
                    continue;
                }
                var parts = line.split(/\s*;\s*/);
                var likeList = parts.length > 1 && parts.some(function (p) { return /Rp|:\s/.test(p); });
                if (likeList) {
                    for (var j = 0; j < parts.length; j++) {
                        html += '<div class="chat-li">' + renderInline(parts[j]) + '</div>';
                    }
                    continue;
                }
                html += '<div class="chat-p">' + renderInline(line) + '</div>';
            }
            return html;
        }

        function addBot(text, images) {
            var row = document.createElement('div');
            row.className = 'chat-msg chat-bot';

            var bubble = document.createElement('div');
            bubble.className = 'chat-bubble';
            bubble.innerHTML = formatBotText(text);

            row.appendChild(bubble);

            var imgs = images || [];
            if (imgs.length) {
                var grid = document.createElement('div');
                grid.className = 'chat-imgs';
                imgs.forEach(function (url) {
                    var a = document.createElement('a');
                    a.href = url;
                    a.target = '_blank';
                    a.rel = 'noopener';
                    a.className = 'chat-img';
                    var img = document.createElement('img');
                    img.src = url;
                    img.alt = 'Contoh hasil jahitan';
                    img.loading = 'lazy';
                    a.appendChild(img);
                    grid.appendChild(a);
                });
                row.appendChild(grid);
            }

            body.appendChild(row);
            scrollBottom();
        }

        function addUser(text) {
            var row = document.createElement('div');
            row.className = 'chat-msg chat-user';

            var bubble = document.createElement('div');
            bubble.className = 'chat-bubble';
            bubble.textContent = text;

            row.appendChild(bubble);
            body.appendChild(row);
            scrollBottom();
        }

        function addTyping() {
            var row = document.createElement('div');
            row.className = 'chat-msg chat-bot';
            row.id = 'chatTyping';

            var bubble = document.createElement('div');
            bubble.className = 'chat-bubble chat-typing';
            bubble.textContent = '...';
            row.appendChild(bubble);

            body.appendChild(row);
            scrollBottom();
        }

        function removeTyping() {
            var t = document.getElementById('chatTyping');
            if (t) { t.parentNode.removeChild(t); }
        }

        addBot('Halo! Saya asisten virtual F3. Tanya apa saja soal layanan jahit, contoh hasil jahitan/galeri, atau status pesanan ya!');

        if (launcher) {
            launcher.addEventListener('click', openChat);
        }
        if (closeBtn) {
            closeBtn.addEventListener('click', closeChat);
        }

        if (form && input) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                var text = input.value.trim();
                if (!text) { return; }
                input.value = '';
                addUser(text);
                addTyping();

                fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                })
                .then(function (res) {
                    return res.json().then(function (data) {
                        return { ok: res.ok, data: data };
                    });
                })
                .then(function (result) {
                    removeTyping();
                    if (!result.ok) {
                        addBot(result.data && result.data.reply ? result.data.reply : 'Maaf, ada kendala. Silakan coba lagi ya.');
                        return;
                    }
                    addBot(result.data.reply, result.data.gambar || []);
                })
                .catch(function () {
                    removeTyping();
                    addBot('Waduh, tidak terhubung ke server. Coba lagi beberapa saat ya.');
                });
            });
        }
    });
})();