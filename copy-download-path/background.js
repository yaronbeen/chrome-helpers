// Notify on every finished download; click the notification (or "Copy path") to copy the full path.

async function copyText(text) {
  if (!(await chrome.offscreen.hasDocument())) {
    await chrome.offscreen.createDocument({
      url: "offscreen.html",
      reasons: ["CLIPBOARD"],
      justification: "Copy download path to clipboard",
    });
  }
  await chrome.runtime.sendMessage({ type: "copy", text });
}

async function copyDownload(id) {
  const [item] = await chrome.downloads.search({ id });
  if (!item || !item.filename) return;
  await copyText(item.filename);
  chrome.notifications.create("copied-" + id + "-" + Date.now(), {
    type: "basic",
    iconUrl: "icon128.png",
    title: "Path copied",
    message: item.filename,
    priority: 0,
  });
}

chrome.downloads.onChanged.addListener(async (delta) => {
  if (delta.state?.current !== "complete") return;
  const [item] = await chrome.downloads.search({ id: delta.id });
  if (!item) return;
  const name = item.filename.split("/").pop();
  chrome.notifications.create("dl-" + item.id, {
    type: "basic",
    iconUrl: "icon128.png",
    title: "Downloaded: " + name,
    message: item.filename,
    buttons: [{ title: "Copy path" }, { title: "Show in folder" }],
    priority: 1,
  });
});

const idFrom = (nid) => (nid.startsWith("dl-") ? Number(nid.slice(3)) : null);

chrome.notifications.onClicked.addListener((nid) => {
  const id = idFrom(nid);
  if (id !== null) copyDownload(id);
  chrome.notifications.clear(nid);
});

chrome.notifications.onButtonClicked.addListener((nid, btn) => {
  const id = idFrom(nid);
  if (id === null) return;
  if (btn === 0) copyDownload(id);
  else chrome.downloads.show(id);
  chrome.notifications.clear(nid);
});

chrome.commands.onCommand.addListener(async (cmd) => {
  if (cmd !== "copy-last") return;
  const [item] = await chrome.downloads.search({ state: "complete", orderBy: ["-endTime"], limit: 1 });
  if (item) copyDownload(item.id);
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "copy-id") copyDownload(msg.id);
});
