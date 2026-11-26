const HOST = "com.yaron.copy_download_path";
const $ = (id) => document.getElementById(id);
const selected = new Map(); // id -> download item
let rows = [];

function status(text, err = false) {
  $("status").textContent = text;
  $("status").className = err ? "err" : "";
}

function refreshBar() {
  const n = selected.size;
  $("count").textContent = `${n} selected`;
  for (const b of ["copySel", "openSel", "zipSel"]) $(b).disabled = n === 0;
  $("all").checked = n > 0 && n === rows.length;
  $("all").indeterminate = n > 0 && n < rows.length;
}

function setSelected(item, row, box, on) {
  box.checked = on;
  row.classList.toggle("sel", on);
  on ? selected.set(item.id, item) : selected.delete(item.id);
}

(async () => {
  const list = $("list");
  const items = await chrome.downloads.search({ state: "complete", orderBy: ["-endTime"], limit: 30 });
  const shown = items.filter((i) => i.filename && i.exists !== false);
  if (!shown.length) {
    list.innerHTML = '<div id="empty">No finished downloads.</div>';
    return;
  }
  for (const item of shown) {
    const row = document.createElement("div");
    row.className = "row";
    const box = document.createElement("input");
    box.type = "checkbox";
    box.onchange = () => { setSelected(item, row, box, box.checked); refreshBar(); };
    const info = document.createElement("div");
    info.className = "name";
    info.title = "Click to select";
    info.textContent = item.filename.split("/").pop();
    info.onclick = () => { setSelected(item, row, box, !box.checked); refreshBar(); };
    const p = document.createElement("div");
    p.className = "path";
    p.textContent = item.filename;
    info.appendChild(p);
    const copy = document.createElement("button");
    copy.textContent = "Copy path";
    copy.onclick = async () => {
      await navigator.clipboard.writeText(item.filename);
      copy.textContent = "Copied ✓";
    };
    const folder = document.createElement("button");
    folder.textContent = "Folder";
    folder.onclick = () => chrome.downloads.show(item.id);
    row.append(box, info, copy, folder);
    list.appendChild(row);
    rows.push({ item, row, box });
  }
  refreshBar();
})();

$("all").onchange = () => {
  const on = $("all").checked;
  for (const r of rows) setSelected(r.item, r.row, r.box, on);
  refreshBar();
};

$("copySel").onclick = async () => {
  const paths = [...selected.values()].map((i) => i.filename);
  await navigator.clipboard.writeText(paths.join("\n"));
  status(`Copied ${paths.length} path(s), one per line.`);
};

$("openSel").onclick = () => {
  // Opens each file with its default app (must run inside the click).
  let n = 0;
  for (const item of selected.values()) {
    try { chrome.downloads.open(item.id); n++; } catch (e) { status(String(e), true); }
  }
  if (n) status(`Opened ${n} file(s).`);
};

$("zipSel").onclick = () => {
  const paths = [...selected.values()].map((i) => i.filename);
  $("zipSel").disabled = true;
  status(`Zipping ${paths.length} file(s)...`);
  chrome.runtime.sendNativeMessage(HOST, { action: "zip", paths }, async (res) => {
    $("zipSel").disabled = selected.size === 0;
    if (chrome.runtime.lastError || !res) {
      return status("Zip helper not reachable: " + (chrome.runtime.lastError?.message || "no reply") +
        " - run install-zip-helper.sh", true);
    }
    if (!res.ok) return status(res.error, true);
    await navigator.clipboard.writeText(res.zip);
    status(`Zipped ${res.count} file(s)${res.missing ? ` (${res.missing} missing, skipped)` : ""} → ${res.zip}  (path copied)`);
  });
};
