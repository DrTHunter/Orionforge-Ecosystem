/* Attach documents to a message box.
 *
 *   const att = attachBox({input, bar, button});   // textarea, a container for chips, a paperclip button
 *   const files = await att.take();                // [{name, b64}]; call att.clear() once the send succeeds
 *
 * Files can be picked, dragged onto the box, or arrive by paste: text longer than
 * LONG_PASTE characters becomes a pasted-text.txt attachment instead of filling the box.
 * A .zip (a whole project) is sent as one file and unpacked on the server.
 */
(function () {
  const LONG_PASTE = 8000;
  const MAX_FILE = 10 * 1024 * 1024, MAX_ALL = 25 * 1024 * 1024;

  function toB64(buf) {
    const bytes = new Uint8Array(buf);
    let bin = '';
    for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
    return btoa(bin);
  }
  function kb(n) { return n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : n >= 1024 ? (n / 1024).toFixed(0) + ' KB' : n + ' B'; }

  window.attachBox = function ({input, bar, button, onError}) {
    const items = [];   // {name, size, file | text}
    const picker = document.createElement('input');
    picker.type = 'file'; picker.multiple = true; picker.style.display = 'none';
    document.body.appendChild(picker);
    const fail = msg => (onError || alert)(msg);

    function total() { return items.reduce((a, i) => a + i.size, 0); }
    function render() {
      bar.innerHTML = '';
      bar.style.display = items.length ? 'flex' : 'none';
      items.forEach((it, idx) => {
        const chip = document.createElement('span');
        chip.style.cssText = 'display:inline-flex;gap:.4rem;align-items:center;font-size:.72rem;padding:.2rem .55rem;border:1px solid var(--bd,#2a2a3a);border-radius:999px;color:var(--mu,#a1a1aa)';
        chip.textContent = '📎 ' + it.name + ' · ' + kb(it.size) + ' ';
        const x = document.createElement('button');
        x.type = 'button'; x.textContent = '×';
        x.style.cssText = 'background:none;border:0;color:inherit;cursor:pointer;font-size:.9rem;padding:0';
        x.onclick = () => { items.splice(idx, 1); render(); };
        chip.appendChild(x);
        bar.appendChild(chip);
      });
    }
    function add(entry) {
      if (entry.size > MAX_FILE) return fail(entry.name + ' is over ' + kb(MAX_FILE));
      if (total() + entry.size > MAX_ALL) return fail('That is more than ' + kb(MAX_ALL) + ' in one message');
      items.push(entry); render();
    }
    function addFiles(list) { Array.from(list).forEach(f => add({name: f.name, size: f.size, file: f})); }

    button.addEventListener('click', () => picker.click());
    picker.addEventListener('change', () => { addFiles(picker.files); picker.value = ''; });
    input.addEventListener('paste', e => {
      const cd = e.clipboardData;
      if (cd && cd.files && cd.files.length) { e.preventDefault(); addFiles(cd.files); return; }
      const text = cd ? cd.getData('text') : '';
      if (text.length > LONG_PASTE) {
        e.preventDefault();
        const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
        const blob = new Blob([text], {type: 'text/plain'});
        add({name: 'pasted-text-' + stamp + '.txt', size: blob.size, file: blob});
      }
    });
    ['dragover', 'drop'].forEach(ev => input.addEventListener(ev, e => {
      if (!e.dataTransfer || !e.dataTransfer.files || (ev === 'dragover' ? !Array.from(e.dataTransfer.types || []).includes('Files') : false)) return;
      e.preventDefault();
      if (ev === 'drop') addFiles(e.dataTransfer.files);
    }));
    render();

    return {
      count: () => items.length,
      async take() {
        const out = [];
        for (const it of items) out.push({name: it.name, b64: toB64(await it.file.arrayBuffer())});
        return out;
      },
      clear() { items.length = 0; render(); },
    };
  };
})();
