// ページ内の絞り込みと全文検索
(() => {
  const norm = (s) => s.toLowerCase().normalize("NFKC");

  // ---- ページ内絞り込み: 見出し単位の <section> を、本文か子セクションが一致するものだけ残す
  const find = document.getElementById("find");
  if (find) {
    const doc = document.querySelector("article.doc");
    const count = document.getElementById("find-count");
    const sections = [...doc.querySelectorAll("section")];
    const own = new Map(sections.map((s) => [s, norm(
      [...s.childNodes].filter((n) => !(n.nodeType === 1 && n.tagName === "SECTION"))
        .map((n) => n.textContent).join(" "))]));
    const tops = sections.filter((s) => !s.parentElement.closest("section"));

    const visit = (s, term) => {
      const selfHit = own.get(s).includes(term);
      let childHit = false;
      for (const c of s.children) if (c.tagName === "SECTION") childHit = visit(c, selfHit ? "" : term) || childHit;
      const show = selfHit || childHit;
      s.hidden = !show;
      return show;
    };
    const apply = () => {
      const term = norm(find.value.trim());
      if (!term) { sections.forEach((s) => (s.hidden = false)); count.textContent = ""; return; }
      let n = 0;
      for (const s of tops) if (visit(s, term)) n++;
      count.textContent = n ? "" : "該当なし";
    };
    find.addEventListener("input", apply);
    const q = new URLSearchParams(location.search).get("q");
    if (q) { find.value = q; apply(); }
  }

  // ---- 全文検索ページ
  const gq = document.getElementById("global-q");
  if (gq && window.SEARCH_INDEX) {
    const list = document.getElementById("results");
    const count = document.getElementById("global-count");
    const index = window.SEARCH_INDEX.map((e) => ({ ...e, n: norm(e.h + " " + e.t) }));
    const escape = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const snippet = (text, term) => {
      const i = norm(text).indexOf(term);
      if (i < 0) return escape(text.slice(0, 140));
      const start = Math.max(0, i - 50);
      return (start ? "…" : "") + escape(text.slice(start, i)) + "<mark>" + escape(text.slice(i, i + term.length)) +
        "</mark>" + escape(text.slice(i + term.length, i + term.length + 90)) + "…";
    };
    const run = () => {
      const term = norm(gq.value.trim());
      history.replaceState(null, "", term ? "?q=" + encodeURIComponent(gq.value.trim()) : location.pathname);
      if (term.length < 2) { list.innerHTML = ""; count.textContent = ""; return; }
      const hits = index.filter((e) => e.n.includes(term));
      count.textContent = hits.length + " 件";
      list.innerHTML = hits.slice(0, 200).map((e) =>
        `<li><a href="${e.u}"><b>${escape(e.h)}</b>` +
        `<small>${escape(e.p)}</small></a><p>${snippet(e.t, term)}</p></li>`).join("");
    };
    gq.addEventListener("input", run);
    const q = new URLSearchParams(location.search).get("q");
    if (q) gq.value = q;
    run();
  }
})();
