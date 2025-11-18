// scrambled-text.js
(function () {
  function createCharSpans(container) {
    const p = container.querySelector('p, h1, h2, h3, h4, h5, h6, span, .scramble-text-content');
    if (!p) return [];
    const text = p.textContent;
    p.textContent = '';
    const chars = [];
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (ch === ' ') {
        const space = document.createTextNode(' ');
        p.appendChild(space);
        continue;
      }
      const span = document.createElement('span');
      span.className = 'char';
      span.dataset.content = ch;
      span.textContent = ch;
      p.appendChild(span);
      chars.push(span);
    }
    return chars;
  }

  function randChar(pool) {
    return pool[Math.floor(Math.random() * pool.length)] || '';
  }

  function scrambleSpan(span, opts) {
    const { duration, scrambleChars } = opts;
    const now = performance.now();
    const endAt = now + duration * 1000;

    if (span.__scrambleRAF) cancelAnimationFrame(span.__scrambleRAF);

    function tick() {
      const t = performance.now();
      if (t >= endAt) {
        span.textContent = span.dataset.content || '';
        span.__scrambleRAF = null;
        return;
      }
      span.textContent = randChar(scrambleChars);
      span.__scrambleRAF = requestAnimationFrame(tick);
    }
    tick();
  }

  function initContainer(container) {
    const radius = parseFloat(container.dataset.radius || container.getAttribute('data-radius')) || 100;
    const duration = parseFloat(container.dataset.duration || container.getAttribute('data-duration')) || 1.2;
    const scrambleChars = (container.dataset.chars || container.getAttribute('data-chars') || '.:').split('');

    const chars = createCharSpans(container);
    if (!chars.length) return;

    function handleMove(e) {
      chars.forEach((c) => {
        const rect = c.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = e.clientX - cx;
        const dy = e.clientY - cy;
        const dist = Math.hypot(dx, dy);
        if (dist < radius) {
          // Lower distance => stronger effect; we scale duration accordingly
          const scale = 1 - dist / radius;
          scrambleSpan(c, { duration: duration * Math.max(0.2, scale), scrambleChars });
        }
      });
    }

    container.addEventListener('pointermove', handleMove);
  }

  function initAll() {
    document.querySelectorAll('.scramble-text').forEach(initContainer);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();
