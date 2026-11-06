(() => {
  "use strict";
  const ns = "http://www.w3.org/2000/svg";
  const chart = document.getElementById("rates-chart");
  const status = document.getElementById("data-status");
  const tooltip = document.getElementById("chart-tooltip");
  const tbody = document.getElementById("observations-body");
  const coverage = document.getElementById("date-coverage");
  const download = document.getElementById("download-csv");
  const code = document.getElementById("starter-code");
  const copy = document.getElementById("copy-code");
  let rows = [];
  let since = 2015;
  let view = "both";

  function el(tag, attrs, text) {
    const e = document.createElementNS(ns, tag);
    Object.entries(attrs || {}).forEach(([key, value]) => e.setAttribute(key, String(value)));
    if (text != null) e.textContent = text;
    return e;
  }

  function number(value) {
    return Number(value).toFixed(2);
  }

  function setMessage(msg) {
    status.textContent = msg;
    status.hidden = !msg;
  }

  function linePath(data, accessor, x, y) {
    return data.map((d, i) => (i ? "L" : "M") + x(i).toFixed(1) + "," + y(accessor(d)).toFixed(1)).join(" ");
  }

  function render() {
    const data = rows.filter(d => Number(d.month.slice(0, 4)) >= since);
    chart.querySelectorAll(".generated").forEach(node => node.remove());
    tooltip.hidden = true;
    if (!data.length) {
      setMessage("The verified source data are temporarily unavailable. No synthetic observations are displayed.");
      return;
    }
    setMessage("");
    const width = 900, height = 420;
    const margin = { left: 57, right: 26, top: 20, bottom: 50 };
    const innerW = width - margin.left - margin.right;
    const innerH = height - margin.top - margin.bottom;
    const values = data.flatMap(d => [
      ...(view !== "repo" ? [d.mortgage] : []),
      ...(view !== "mortgage" ? [d.repo] : [])
    ]);
    const vmax = Math.max(1, Math.ceil((Math.max(...values) + .2) / 2) * 2);
    const x = i => margin.left + (data.length <= 1 ? 0 : i * innerW / (data.length - 1));
    const y = v => margin.top + innerH * (1 - v / vmax);
    const g = el("g", { class: "generated" });

    for (let tick = 0; tick <= vmax; tick += 2) {
      const py = y(tick);
      g.append(el("line", { x1: margin.left, x2: width - margin.right, y1: py, y2: py, class: "grid-line" }));
      g.append(el("text", { x: margin.left - 11, y: py + 4, "text-anchor": "end", class: "axis-label" }, String(tick)));
    }
    g.append(el("text", { x: margin.left, y: 12, class: "axis-label" }, "% p.a."));
    const step = Math.max(1, Math.ceil(data.length / 8));
    data.forEach((d, i) => {
      if (i % step !== 0 && i !== data.length - 1) return;
      g.append(el("text", { x: x(i), y: height - 17, class: "axis-label", "text-anchor": "middle" }, d.month.slice(0, 4) + (step < 12 ? "-" + d.month.slice(5) : "")));
    });

    if (view !== "repo") g.append(el("path", { d: linePath(data, d => d.mortgage, x, y), class: "data-line mortgage-line" }));
    if (view !== "mortgage") g.append(el("path", { d: linePath(data, d => d.repo, x, y), class: "data-line repo-line" }));
    const crosshair = el("line", { x1: 0, x2: 0, y1: margin.top, y2: height - margin.bottom, class: "crosshair", opacity: 0 });
    const mortgageDot = el("circle", { r: 6, class: "data-dot", fill: "#147f7b", opacity: 0 });
    const repoDot = el("circle", { r: 6, class: "data-dot", fill: "#d78b56", opacity: 0 });
    g.append(crosshair, mortgageDot, repoDot);
    chart.append(g);

    function showAt(i, clientX, clientY) {
      const d = data[i];
      const px = x(i);
      crosshair.setAttribute("x1", px);
      crosshair.setAttribute("x2", px);
      crosshair.setAttribute("opacity", "1");
      mortgageDot.setAttribute("cx", px);
      mortgageDot.setAttribute("cy", y(d.mortgage));
      mortgageDot.setAttribute("opacity", view !== "repo" ? "1" : "0");
      repoDot.setAttribute("cx", px);
      repoDot.setAttribute("cy", y(d.repo));
      repoDot.setAttribute("opacity", view !== "mortgage" ? "1" : "0");
      tooltip.textContent = d.month + "  ·  Mortgage: " + number(d.mortgage) + "%  ·  Repo: " + number(d.repo) + "%";
      tooltip.hidden = false;
      const parent = chart.parentElement.getBoundingClientRect();
      tooltip.style.left = Math.min(Math.max(clientX - parent.left + 8, 0), parent.width - 190) + "px";
      tooltip.style.top = Math.max(0, clientY - parent.top - 65) + "px";
    }

    chart.onpointermove = event => {
      const rect = chart.getBoundingClientRect();
      const px = (event.clientX - rect.left) * width / rect.width;
      const i = Math.max(0, Math.min(data.length - 1, Math.round((px - margin.left) * (data.length - 1) / innerW)));
      showAt(i, event.clientX, event.clientY);
    };
    chart.onpointerleave = () => {
      tooltip.hidden = true;
      crosshair.setAttribute("opacity", "0");
      mortgageDot.setAttribute("opacity", "0");
      repoDot.setAttribute("opacity", "0");
    };
  }

  function makeCsv() {
    const header = "month,mortgage_new_business_AAR_percent,repo_2w_month_end_percent";
    const content = header + "\n" + rows.map(d => [d.month, d.mortgage, d.repo].join(",")).join("\n") + "\n";
    const blob = new Blob([content], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "czech-mortgage-vs-policy-rates.csv";
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }

  document.getElementById("range-buttons").addEventListener("click", event => {
    const b = event.target.closest("button[data-since]");
    if (!b) return;
    since = Number(b.dataset.since);
    document.querySelectorAll("[data-since]").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    render();
  });

  document.getElementById("view-buttons").addEventListener("click", event => {
    const b = event.target.closest("button[data-view]");
    if (!b) return;
    view = b.dataset.view;
    document.querySelectorAll("[data-view]").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    render();
  });

  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code.textContent.trim());
      copy.textContent = "Copied ✓";
      setTimeout(() => { copy.textContent = "Copy starter code"; }, 2200);
    } catch (_) {
      copy.textContent = "Select the code to copy";
    }
  });
  download.addEventListener("click", makeCsv);

  fetch("./data.json", { cache: "no-cache" }).then(response => {
    if (!response.ok) throw new Error("Data file unavailable");
    return response.json();
  }).then(data => {
    if (data.status !== "verified" || !Array.isArray(data.rows) || data.rows.length < 80) {
      throw new Error("Data not verified");
    }
    rows = data.rows.filter(d =>
      /^\d{4}-\d{2}$/.test(d.month) && Number.isFinite(d.repo) && Number.isFinite(d.mortgage)
    );
    if (rows.length < 80) throw new Error("Not enough valid observations");
    rows.sort((a, b) => a.month.localeCompare(b.month));
    download.disabled = false;
    coverage.textContent = rows[0].month + " to " + rows[rows.length - 1].month + " · source checked " + data.updated;
    tbody.replaceChildren();
    rows.forEach(d => {
      const tr = document.createElement("tr");
      [d.month, number(d.mortgage), number(d.repo)].forEach(s => {
        const td = document.createElement("td"); td.textContent = s; tr.append(td);
      });
      tbody.append(tr);
    });
    const latest = rows[rows.length - 1];
    const previousYear = rows.find(d => d.month === String(Number(latest.month.slice(0, 4)) - 1) + latest.month.slice(4));
    document.getElementById("mortgage-month").textContent = latest.month;
    document.getElementById("latest-mortgage").textContent = number(latest.mortgage);
    document.getElementById("latest-repo").textContent = number(latest.repo);
    document.getElementById("yearly-change").textContent = previousYear
      ? (latest.mortgage - previousYear.mortgage >= 0 ? "+" : "") + number(latest.mortgage - previousYear.mortgage)
      : "n/a";
    document.getElementById("story-highlights").hidden = false;
    render();
  }).catch(error => {
    console.warn("Mortgage story: verified feed not available", error);
    rows = [];
    coverage.textContent = "Verified data unavailable · Source links and reproduction method remain accessible";
    setMessage("We could not load the verified data series. The chart is intentionally blank rather than showing approximated figures.");
  });
})();
