// TODO ページの検索・絞り込み (他ページでは何もしない)
(() => {
  const q = document.getElementById("q");
  if (!q) return;
  const hideDone = document.getElementById("hide-done");
  const chips = [...document.querySelectorAll(".chip")];
  const sections = [...document.querySelectorAll("section.category")];
  const noResults = document.getElementById("no-results");
  // ?cat=<id> のほか、クエリを渡せない環境向けに #<id> でも受け付ける
  let cat = new URLSearchParams(location.search).get("cat") || decodeURIComponent(location.hash.slice(1));

  const load = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
  const save = (k, v) => { try { localStorage.setItem(k, v); } catch {} };
  hideDone.checked = load("hideDone") === "1";

  function apply() {
    const term = q.value.trim().toLowerCase();
    let anyVisible = false;
    for (const s of sections) {
      let visibleRows = 0;
      for (const tr of s.querySelectorAll("tbody tr")) {
        const show = (!term || tr.dataset.search.includes(term)) &&
                     !(hideDone.checked && tr.classList.contains("done"));
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
  apply();
})();
