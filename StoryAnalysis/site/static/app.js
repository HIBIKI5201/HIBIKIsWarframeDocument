// ページ内の絞り込みと全文検索
(() => {
  const norm = (s) => s.toLowerCase().normalize("NFKC");
  const params = new URLSearchParams(location.search);
  const escape = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // 固定ヘッダーの高さ（折り返しで変わる）に合わせて、検索欄の固定位置とアンカーの余白を決める
  const header = document.querySelector(".site-header");
  if (header) {
    const fit = () => document.documentElement.style.setProperty("--header-h", header.offsetHeight + "px");
    fit();
    addEventListener("resize", fit);
  }

  // URL の ?q= を書き換える（履歴は増やさない）
  const setParam = (key, value) => {
    const p = new URLSearchParams(location.search);
    if (value) p.set(key, value); else p.delete(key);
    const qs = p.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
  };

  // ---- ページ内絞り込み: 見出し単位の <section> と表の行を、一致するものだけ残す
  // 見出しや本文が一致したセクションは丸ごと、表の行だけが一致したセクションはその行だけを表示する
  const find = document.getElementById("find");
  if (find) {
    const doc = document.querySelector("article.doc");
    const count = document.getElementById("find-count");
    const sections = [...doc.querySelectorAll("section")];
    const isOwn = (n) => !(n.nodeType === 1 && (n.tagName === "SECTION" || n.querySelector?.("table") || n.tagName === "TABLE"));
    const own = new Map(sections.map((s) => [s, norm([...s.childNodes].filter(isOwn).map((n) => n.textContent).join(" "))]));
    const rows = new Map(sections.map((s) => [s, [...s.querySelectorAll(":scope > .table-wrap tbody tr, :scope > table tbody tr")]
      .map((tr) => [tr, norm(tr.textContent)])]));
    const tops = sections.filter((s) => !s.parentElement.closest("section"));

    const visit = (s, term) => {
      const selfHit = !term || own.get(s).includes(term);
      let rowHit = false;
      for (const [tr, text] of rows.get(s)) {
        const hit = selfHit || text.includes(term);
        tr.hidden = !hit;
        rowHit ||= hit;
      }
      let childHit = false;
      for (const c of s.children) if (c.tagName === "SECTION") childHit = visit(c, selfHit ? "" : term) || childHit;
      const show = selfHit || rowHit || childHit;
      s.hidden = !show;
      return show;
    };
    const apply = () => {
      const term = norm(find.value.trim());
      setParam("q", find.value.trim());
      let n = 0;
      for (const s of tops) if (visit(s, term)) n++;
      count.textContent = term && !n ? "該当なし" : "";
    };
    find.addEventListener("input", apply);
    if (params.get("q")) { find.value = params.get("q"); apply(); }
  }

  // ---- 全文検索ページ
  const gq = document.getElementById("global-q");
  if (gq && window.SEARCH_INDEX) {
    const list = document.getElementById("results");
    const ents = document.getElementById("entities");
    const chips = document.getElementById("kinds");
    const count = document.getElementById("global-count");
    const index = window.SEARCH_INDEX.map((e) => ({ ...e, n: norm(e.h + " " + e.t), hn: norm(e.h) }));
    const entities = (window.ENTITIES || []).map((e) => ({ ...e, nn: e.n.map(norm) }));
    const kinds = ["すべて", ...new Set(index.map((e) => e.k))];
    let kind = kinds.includes(params.get("type")) ? params.get("type") : "すべて";

    const snippet = (text, term) => {
      const i = norm(text).indexOf(term);
      if (i < 0) return escape(text.slice(0, 140));
      const start = Math.max(0, i - 50);
      return (start ? "…" : "") + escape(text.slice(start, i)) + "<mark>" + escape(text.slice(i, i + term.length)) +
        "</mark>" + escape(text.slice(i + term.length, i + term.length + 90)) + "…";
    };
    const run = () => {
      const raw = gq.value.trim();
      const term = norm(raw);
      setParam("q", raw);
      setParam("type", kind === "すべて" ? "" : kind);
      if (term.length < 2) { list.innerHTML = ents.innerHTML = count.textContent = ""; renderChips({}); return; }
      const hits = index.filter((e) => e.n.includes(term));
      const perKind = {};
      for (const e of hits) perKind[e.k] = (perKind[e.k] || 0) + 1;
      renderChips(perKind, hits.length);
      // 見出しが一致するもの（そのページ・節が本題）を先に出す
      const shown = hits.filter((e) => kind === "すべて" || e.k === kind)
        .sort((a, b) => (b.hn.includes(term) - a.hn.includes(term)));
      count.textContent = shown.length + " 件";
      list.innerHTML = shown.slice(0, 200).map((e) =>
        `<li><a href="${e.u}"><b>${escape(e.h)}</b>` +
        `<small>${escape(e.k)} · ${escape(e.p)}</small></a><p>${snippet(e.t, term)}</p></li>`).join("");
      // 名前が一致するキャラクター・クエストは、ページへの近道を上に出す
      const matched = entities.filter((e) => (kind === "すべて" || e.k === kind) && e.nn.some((n) => n.includes(term)))
        .sort((a, b) => (b.nn.some((n) => n === term) - a.nn.some((n) => n === term)) || b.c - a.c).slice(0, 8);
      ents.innerHTML = matched.map((e) =>
        `<li><a href="${e.u}"><span class="kind">${escape(e.k)}</span><b>${escape(e.n[0])}</b>` +
        (e.n[1] && e.k === "クエスト" ? `<small>${escape(e.n[1])}</small>` : "") +
        `<small>${escape(e.g)}</small></a><p>${escape(e.s)}</p></li>`).join("");
    };
    const renderChips = (perKind, total) => {
      chips.innerHTML = kinds.map((k) => {
        const n = k === "すべて" ? total : perKind[k];
        return `<button type="button" data-kind="${escape(k)}" aria-pressed="${k === kind}">${escape(k)}` +
          (n ? ` <small>${n}</small>` : "") + "</button>";
      }).join("");
    };
    chips.addEventListener("click", (ev) => {
      const b = ev.target.closest("button");
      if (!b) return;
      kind = b.dataset.kind;
      run();
    });
    gq.addEventListener("input", run);
    if (params.get("q")) gq.value = params.get("q");
    run();
  }
})();
