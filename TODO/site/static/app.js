// TODO ページの検索・絞り込みと編集モード (他ページでは何もしない)
(() => {
  const q = document.getElementById("q");
  if (!q) return;
  const hideDone = document.getElementById("hide-done");
  const chips = [...document.querySelectorAll(".chip")];
  const sections = [...document.querySelectorAll("section.category")];
  const noResults = document.getElementById("no-results");
  const editBtn = document.getElementById("edit-mode");
  const editHint = document.getElementById("edit-hint");
  const toast = document.getElementById("toast");
  let cat = new URLSearchParams(location.search).get("cat") || "";

  const load = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
  const save = (k, v) => { try { localStorage.setItem(k, v); } catch {} };
  hideDone.checked = load("hideDone") === "1";

  function apply() {
    const term = q.value.trim().toLowerCase();
    const editing = document.body.classList.contains("editing");
    let anyVisible = false;
    for (const s of sections) {
      let visibleRows = 0;
      for (const tr of s.querySelectorAll("tbody tr")) {
        // 編集中は、操作した行が即座に消えないよう「完了を隠す」を効かせない
        const show = (!term || tr.dataset.search.includes(term)) &&
                     !(hideDone.checked && !editing && tr.classList.contains("done"));
        tr.hidden = !show;
        if (show) visibleRows++;
      }
      s.hidden = (cat && s.dataset.cat !== cat) || visibleRows === 0;
      anyVisible ||= !s.hidden;
    }
    for (const c of chips) c.classList.toggle("active", c.dataset.cat === cat);
    noResults.hidden = anyVisible;
  }

  q.addEventListener("input", apply);
  hideDone.addEventListener("change", () => { save("hideDone", hideDone.checked ? "1" : "0"); apply(); });
  for (const c of chips) c.addEventListener("click", () => {
    cat = c.dataset.cat;
    history.replaceState(null, "", cat ? "?cat=" + cat : location.pathname);
    apply();
  });

  // ---------------------------------------------------------------- 編集モード

  function setEditing(on) {
    document.body.classList.toggle("editing", on);
    editBtn.setAttribute("aria-pressed", String(on));
    editHint.hidden = !on;
    save("editing", on ? "1" : "0");
    apply();
  }

  let toastTimer;
  function showToast(msg) {
    toast.textContent = msg;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toast.hidden = true; }, 4000);
  }

  // 行の状態に合わせて、カテゴリ見出しの件数・進捗バーとチップの残り件数を更新する
  function refreshCounts(section) {
    const rows = section.querySelectorAll("tbody tr");
    const done = section.querySelectorAll("tbody tr.done").length;
    section.querySelector(".done-n").textContent = done;
    const pct = rows.length ? Math.round(done * 100 / rows.length) : 0;
    const bar = section.querySelector("header .bar");
    bar.setAttribute("aria-valuenow", pct);
    bar.firstElementChild.style.width = pct + "%";
    const chip = chips.find((c) => c.dataset.cat === section.dataset.cat);
    if (chip) chip.querySelector("small").textContent = rows.length - done;
  }

  async function update(tr, action) {
    const section = tr.closest("section.category");
    tr.classList.add("busy");
    try {
      const res = await fetch("/api/item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: section.dataset.cat, name: tr.dataset.name, action }),
      });
      const item = await res.json();
      if (!res.ok) throw new Error(item.error || res.statusText);
      tr.classList.toggle("done", item.done);
      tr.querySelector(".check").setAttribute("aria-pressed", String(item.done));
      const qty = tr.querySelector(".qty");
      if (qty && item.required !== null) qty.textContent = "×" + item.required;
      const time = tr.querySelector("time.updated");
      if (time && item.updated) time.textContent = item.updated;
      refreshCounts(section);
    } catch (e) {
      showToast("保存できませんでした: " + e.message);
    } finally {
      tr.classList.remove("busy");
    }
  }

  document.addEventListener("click", (e) => {
    if (!document.body.classList.contains("editing")) return;
    const btn = e.target.closest("button.check:not([disabled]), button.step");
    const tr = btn && btn.closest("tr");
    if (!tr || tr.classList.contains("busy")) return;
    update(tr, btn.classList.contains("check") ? "toggle" : btn.dataset.action);
  });

  // 書き込み API は serve.py で配信しているときだけ使える
  fetch("/api/ping").then((r) => r.ok && r.json()).then((ok) => {
    if (!ok) return;
    editBtn.hidden = false;
    editBtn.addEventListener("click", () => setEditing(!document.body.classList.contains("editing")));
    if (load("editing") === "1") setEditing(true);
  }).catch(() => {});

  apply();
})();
