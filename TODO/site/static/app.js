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
  // ?cat=<id> のほか、クエリを渡せない環境向けに #<id> でも受け付ける
  let cat = new URLSearchParams(location.search).get("cat") || decodeURIComponent(location.hash.slice(1));

  const load = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
  const save = (k, v) => { try { localStorage.setItem(k, v); } catch {} };
  hideDone.checked = load("hideDone") === "1";

  // 項目の行の直後に並ぶ、その項目のパーツの行
  function partRows(tr) {
    const rows = [];
    for (let r = tr.nextElementSibling; r && r.classList.contains("part-row"); r = r.nextElementSibling) rows.push(r);
    return rows;
  }

  function apply() {
    const term = q.value.trim().toLowerCase();
    const editing = document.body.classList.contains("editing");
    let anyVisible = false;
    for (const s of sections) {
      let visibleRows = 0;
      for (const d of s.querySelectorAll("details.done-list")) {
        // 検索中は、完了済みの一覧に該当があれば開いて見せる
        const hit = [...d.querySelectorAll("tr.item")].some((tr) => !term || tr.dataset.search.includes(term));
        d.hidden = !hit || (hideDone.checked && !editing);
        if (term && hit) d.open = true;
      }
      for (const tr of s.querySelectorAll("tbody tr.item")) {
        // 編集中は、操作した行が即座に消えないよう「完了を隠す」を効かせない
        const show = (!term || tr.dataset.search.includes(term)) &&
                     !(hideDone.checked && !editing && tr.classList.contains("done"));
        tr.hidden = !show;
        for (const r of partRows(tr)) r.hidden = !show;
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
    const rows = section.querySelectorAll("tbody tr.item");
    const done = section.querySelectorAll("tbody tr.item.done").length;
    for (const n of section.querySelectorAll(".done-n")) n.textContent = done;
    const pct = rows.length ? Math.round(done * 100 / rows.length) : 0;
    const bar = section.querySelector("header .bar");
    bar.setAttribute("aria-valuenow", pct);
    bar.firstElementChild.style.width = pct + "%";
    const chip = chips.find((c) => c.dataset.cat === section.dataset.cat);
    if (chip) chip.querySelector("small").textContent = rows.length - done;
  }

  async function update(tr, action, index) {
    const section = tr.closest("section.category");
    tr.classList.add("busy");
    try {
      const res = await fetch("/api/item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category: section.dataset.cat, name: tr.dataset.name, action, index }),
      });
      const item = await res.json();
      if (!res.ok) throw new Error(item.error || res.statusText);
      tr.classList.toggle("done", item.done);
      tr.querySelector(".check:not(.part)").setAttribute("aria-pressed", String(item.done));
      partRows(tr).forEach((r, k) => {
        r.classList.toggle("done", item.parts[k]);
        r.querySelector(".part").setAttribute("aria-pressed", String(item.parts[k]));
      });
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
    let tr = btn && btn.closest("tr");
    // パーツの行で押されたら、その上にある項目の行を対象にする
    while (tr && tr.classList.contains("part-row")) tr = tr.previousElementSibling;
    if (!tr || tr.classList.contains("busy")) return;
    if (btn.classList.contains("part")) update(tr, "part", Number(btn.dataset.index));
    else update(tr, btn.classList.contains("check") ? "toggle" : btn.dataset.action);
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
