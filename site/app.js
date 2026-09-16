const money = (n) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);

const moneyExact = (n) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(n);

const pct = (ratio) => {
  if (ratio === null || ratio === undefined || Number.isNaN(ratio)) return "—";
  const sign = ratio > 0 ? "+" : "";
  return `${sign}${Math.round(ratio * 100)}%`;
};

const alertLabels = {
  spend_spike: "Spend spike",
  service_growth: "Service growth",
  open_actions: "Open actions",
  label_compliance_drift: "Label drift",
};

function momClass(ratio, isNew) {
  if (isNew) return "mom new";
  if (ratio === null || ratio === undefined) return "mom flat";
  if (ratio > 0.02) return "mom up";
  if (ratio < -0.02) return "mom down";
  return "mom flat";
}

function renderHeroChart(svg, services) {
  const width = 640;
  const height = 420;
  const pad = 24;
  const top = services.slice(0, 6);
  const max = Math.max(
    ...top.map((s) => Math.max(s.subtotal_usd, s.prior_usd || 0)),
    1
  );
  const gap = 18;
  const barW = (width - pad * 2 - gap * (top.length - 1)) / top.length;
  const pairGap = 4;
  const half = (barW - pairGap) / 2;

  const bars = top
    .map((s, i) => {
      const prior = s.prior_usd ?? 0;
      const hNow = ((s.subtotal_usd / max) * (height - 80)) | 0;
      const hPrior = ((prior / max) * (height - 80)) | 0;
      const x = pad + i * (barW + gap);
      const yNow = height - 36 - hNow;
      const yPrior = height - 36 - hPrior;
      const label = s.name.split(" ").slice(0, 2).join(" ");
      return `
        <g>
          <rect class="bar prior" x="${x}" y="${yPrior}" width="${half}" height="${hPrior}" fill="#94a3b8" rx="2"/>
          <rect class="bar" x="${x + half + pairGap}" y="${yNow}" width="${half}" height="${hNow}" fill="#0e7490" rx="2"/>
          <text x="${x + barW / 2}" y="${height - 12}" text-anchor="middle" fill="#334155" font-size="11" font-family="IBM Plex Sans, sans-serif" font-weight="600">${label}</text>
        </g>`;
    })
    .join("");

  svg.innerHTML = `
    <g font-family="IBM Plex Sans, sans-serif" font-size="12" fill="#64748b">
      <rect x="24" y="12" width="12" height="12" fill="#94a3b8"/>
      <text x="42" y="22">Prior</text>
      <rect x="90" y="12" width="12" height="12" fill="#0e7490"/>
      <text x="108" y="22">Current</text>
    </g>
    ${bars}`;
}

function renderOutcomeStrip(el, data) {
  const items = [
    { label: "Invoice", value: money(data.invoice_total_usd) },
    { label: "MoM", value: pct(data.invoice_mom_ratio), tone: momClass(data.invoice_mom_ratio, false) },
    { label: "Addressable", value: money(data.opportunity_total_usd) },
    { label: "Open actions", value: String(data.open_actions ?? (data.actions || []).length) },
  ];
  el.innerHTML = items
    .map(
      (item) => `
      <div class="outcome">
        <span class="outcome-label">${item.label}</span>
        <span class="outcome-value ${item.tone || ""}">${item.value}</span>
      </div>`
    )
    .join("");
}

function renderMetrics(el, data) {
  const mom = data.invoice_mom_ratio;
  const items = [
    { label: "Invoice total", value: money(data.invoice_total_usd) },
    { label: "Vs prior period", value: pct(mom), tone: momClass(mom, false) },
    {
      label: "Top driver share",
      value: `${Math.round((data.top_driver?.share || 0) * 100)}%`,
    },
  ];
  el.innerHTML = items
    .map(
      (item) => `
      <div class="metric">
        <span class="label">${item.label}</span>
        <span class="value ${item.tone || ""}">${item.value}</span>
      </div>`
    )
    .join("");
}

function renderSpendCompare(el, data) {
  const prior = data.prior_invoice_usd;
  const current = data.invoice_total_usd;
  const mom = data.invoice_mom_ratio;
  if (!prior) {
    el.innerHTML = "";
    return;
  }
  const max = Math.max(prior, current, 1);
  el.innerHTML = `
    <div class="compare-bars">
      <div class="compare-row">
        <span class="compare-label">Prior</span>
        <div class="compare-track"><div class="compare-fill prior" style="--w:${(prior / max) * 100}%"></div></div>
        <span class="compare-amt">${moneyExact(prior)}</span>
      </div>
      <div class="compare-row">
        <span class="compare-label">Current</span>
        <div class="compare-track"><div class="compare-fill now" style="--w:${(current / max) * 100}%"></div></div>
        <span class="compare-amt">${moneyExact(current)}</span>
      </div>
    </div>
    <p class="compare-note">
      Comparable Google Cloud services ${pct(mom)} period over period
      (${money(prior)} → ${money(current)}). New services are included in current total only.
    </p>`;
}

function renderDrivers(el, services) {
  const max = Math.max(...services.map((s) => s.subtotal_usd), 1);
  el.innerHTML = services
    .slice(0, 6)
    .map((s) => {
      const width = Math.max(4, (s.subtotal_usd / max) * 100);
      const delta = s.is_new ? "New" : pct(s.mom_ratio);
      const sid = s.service_id ? `<span class="sid">${s.service_id}</span>` : "";
      return `
        <div class="driver-row">
          <span class="name">${s.name}${sid}</span>
          <div class="driver-track"><div class="driver-fill" style="--w:${width}%"></div></div>
          <span class="amt">${moneyExact(s.subtotal_usd)}</span>
          <span class="${momClass(s.mom_ratio, s.is_new)}">${delta}</span>
        </div>`;
    })
    .join("");
}

function renderTrendList(el, rows, emptyLabel) {
  if (!rows?.length) {
    el.innerHTML = `<p class="trend-empty">${emptyLabel}</p>`;
    return;
  }
  el.innerHTML = rows
    .map((s) => {
      const prior = s.prior_usd;
      const max = Math.max(s.subtotal_usd, prior || 0, 1);
      const nowW = Math.max(4, (s.subtotal_usd / max) * 100);
      const priorW = prior == null ? 0 : Math.max(4, (prior / max) * 100);
      return `
        <div class="trend-item">
          <div class="trend-top">
            <strong>${s.name}</strong>
            <span class="${momClass(s.mom_ratio, s.is_new)}">${s.is_new ? "New" : pct(s.mom_ratio)}</span>
          </div>
          <div class="mini-compare">
            <div class="mini-track"><div class="mini-fill prior" style="width:${priorW}%"></div></div>
            <div class="mini-track"><div class="mini-fill now" style="width:${nowW}%"></div></div>
          </div>
          <div class="trend-amts">
            <span>${prior == null ? "—" : moneyExact(prior)}</span>
            <span>${moneyExact(s.subtotal_usd)}</span>
          </div>
        </div>`;
    })
    .join("");
}

const typeLabels = {
  growth_anomaly: "MoM growth spike",
  discount_gap: "Discount / CU coverage",
  new_service_review: "New service ownership",
  idle_candidate: "Possible idle spend",
};

function renderOpportunities(elBreakdown, elList, actions, totalUsd) {
  const byType = {};
  for (const a of actions || []) {
    const key = a.type || "other";
    if (!byType[key]) byType[key] = { count: 0, savings: 0 };
    byType[key].count += 1;
    byType[key].savings += a.est_monthly_savings_usd || 0;
  }
  const types = Object.entries(byType).sort((a, b) => b[1].savings - a[1].savings);
  const maxType = Math.max(...types.map(([, v]) => v.savings), 1);

  elBreakdown.innerHTML = types
    .map(([type, v]) => {
      const label = typeLabels[type] || type;
      const share = totalUsd ? Math.round((v.savings / totalUsd) * 100) : 0;
      return `
        <div class="opp-type">
          <div class="opp-type-top">
            <strong>${label}</strong>
            <span class="opp-type-amt">${moneyExact(v.savings)} · ${v.count}</span>
          </div>
          <div class="opp-type-track">
            <div class="opp-type-fill" style="--w:${Math.max(6, (v.savings / maxType) * 100)}%"></div>
          </div>
          <span class="opp-type-share">${share}% of addressable</span>
        </div>`;
    })
    .join("");

  const ranked = [...(actions || [])].sort(
    (a, b) => (b.est_monthly_savings_usd || 0) - (a.est_monthly_savings_usd || 0)
  );
  elList.innerHTML = ranked
    .map((a) => {
      const why = typeLabels[a.type] || a.type;
      return `
      <article class="opp-item" role="listitem">
        <div class="opp-item-main">
          <h3>${a.service}</h3>
          <p>${why}${a.service_id ? ` · ${a.service_id}` : ""}</p>
        </div>
        <div class="opp-item-save">${moneyExact(a.est_monthly_savings_usd)}/mo</div>
      </article>`;
    })
    .join("");
}

function renderQueue(el, actions) {
  el.innerHTML = actions
    .map((a) => {
      const owner = a.owner_label || a.owner;
      const sid = a.service_id ? ` · ${a.service_id}` : "";
      return `
      <article class="queue-item" role="listitem">
        <div class="score">${a.priority_score}</div>
        <div>
          <h3>${a.service}</h3>
          <p>${a.message}</p>
          <p class="meta">${owner}${sid}</p>
        </div>
        <div class="savings">${moneyExact(a.est_monthly_savings_usd)}/mo</div>
      </article>`;
    })
    .join("");
}

function renderAlerts(el, alerts) {
  el.innerHTML = Object.entries(alerts)
    .map(([key, value]) => {
      const on = value === 1;
      return `<div class="alert-pill ${on ? "on" : "off"}">${alertLabels[key] || key}: ${
        on ? "ACTIVE" : "OK"
      }</div>`;
    })
    .join("");
}

function renderPareto(stripEl, chartEl, pareto) {
  if (!pareto) {
    stripEl.innerHTML = "";
    chartEl.innerHTML = "";
    return;
  }
  stripEl.innerHTML = [
    { label: "Top 5 share", value: `${Math.round((pareto.top5_share || 0) * 100)}%` },
    { label: "Services to 50%", value: String(pareto.services_for_50_pct) },
    { label: "Services to 80%", value: String(pareto.services_for_80_pct) },
  ]
    .map(
      (item) => `
      <div class="metric">
        <span class="label">${item.label}</span>
        <span class="value">${item.value}</span>
      </div>`
    )
    .join("");

  chartEl.innerHTML = (pareto.rows || [])
    .map((r) => {
      const shareW = Math.max(4, (r.share || 0) * 100);
      const cumW = Math.max(4, (r.cumulative_share || 0) * 100);
      const sid = r.service_id ? `<span class="sid">${r.service_id}</span>` : "";
      return `
        <div class="pareto-row">
          <span class="pareto-rank">${r.rank}</span>
          <span class="name">${r.name}${sid}</span>
          <div class="pareto-tracks">
            <div class="pareto-track"><div class="pareto-fill share" style="--w:${shareW}%"></div></div>
            <div class="pareto-track"><div class="pareto-fill cum" style="--w:${cumW}%"></div></div>
          </div>
          <span class="amt">${moneyExact(r.subtotal_usd)}</span>
          <span class="pareto-cum">${Math.round((r.cumulative_share || 0) * 100)}%</span>
        </div>`;
    })
    .join("");
}

function renderSavings(stripEl, listEl, savings) {
  if (!savings) {
    stripEl.innerHTML = "";
    listEl.innerHTML = "";
    return;
  }
  const realized = savings.realized_savings_usd || 0;
  stripEl.innerHTML = [
    { label: "List cost", value: money(savings.list_cost_usd) },
    {
      label: "Recorded savings",
      value: moneyExact(realized),
      tone: realized < 0 ? "mom down" : "",
    },
    {
      label: "Coverage of list",
      value: `${Math.round((savings.coverage_ratio || 0) * 1000) / 10}%`,
    },
  ]
    .map(
      (item) => `
      <div class="metric">
        <span class="label">${item.label}</span>
        <span class="value ${item.tone || ""}">${item.value}</span>
      </div>`
    )
    .join("");

  if (!(savings.lines || []).length) {
    listEl.innerHTML = `<p class="trend-empty">No discount lines above the demo threshold.</p>`;
    return;
  }
  listEl.innerHTML = savings.lines
    .map((line) => {
      const sid = line.service_id ? ` · ${line.service_id}` : "";
      return `
      <article class="savings-item" role="listitem">
        <div>
          <h3>${line.name}</h3>
          <p>Other / negotiated / programs${sid}</p>
        </div>
        <div class="savings-amt">${moneyExact(line.total_savings_usd)}</div>
      </article>`;
    })
    .join("");
}

function renderAllocation(stripEl, gapsEl, allocation) {
  if (!allocation) {
    stripEl.innerHTML = "";
    gapsEl.innerHTML = "";
    return;
  }
  stripEl.innerHTML = [
    {
      label: "Tagged spend",
      value: `${Math.round((allocation.compliance_ratio || 0) * 100)}%`,
    },
    { label: "Unowned spend", value: money(allocation.unowned_spend_usd) },
    { label: "Gaps", value: String(allocation.unowned_service_count) },
  ]
    .map(
      (item) => `
      <div class="metric">
        <span class="label">${item.label}</span>
        <span class="value">${item.value}</span>
      </div>`
    )
    .join("");

  gapsEl.innerHTML = (allocation.gaps || [])
    .map((g) => {
      const sid = g.service_id ? `<span class="sid">${g.service_id}</span>` : "";
      return `
      <article class="gap-item" role="listitem">
        <div>
          <h3>${g.name}${sid}</h3>
          <p>Needs an owner tag</p>
        </div>
        <div class="gap-amt">${moneyExact(g.subtotal_usd)}</div>
      </article>`;
    })
    .join("");
}

function renderForecast(stripEl, compareEl, forecast, currentInvoice) {
  if (!forecast) {
    stripEl.innerHTML = "";
    compareEl.innerHTML = "";
    return;
  }
  stripEl.innerHTML = [
    { label: "Projected next", value: money(forecast.next_invoice_usd) },
    {
      label: "Projected delta",
      value: moneyExact(forecast.projected_delta_usd),
      tone: momClass(
        forecast.projected_delta_usd > 0 ? 0.1 : forecast.projected_delta_usd < 0 ? -0.1 : 0,
        false
      ),
    },
    {
      label: "Runway if recovered",
      value: `${forecast.runway_months_if_recovered} mo`,
    },
  ]
    .map(
      (item) => `
      <div class="metric">
        <span class="label">${item.label}</span>
        <span class="value ${item.tone || ""}">${item.value}</span>
      </div>`
    )
    .join("");

  const current = currentInvoice || 0;
  const next = forecast.next_invoice_usd || 0;
  const recovered = forecast.next_invoice_if_recovered_usd || 0;
  const max = Math.max(current, next, recovered, 1);
  compareEl.innerHTML = `
    <div class="compare-bars">
      <div class="compare-row">
        <span class="compare-label">Current</span>
        <div class="compare-track"><div class="compare-fill prior" style="--w:${(current / max) * 100}%"></div></div>
        <span class="compare-amt">${moneyExact(current)}</span>
      </div>
      <div class="compare-row">
        <span class="compare-label">Next</span>
        <div class="compare-track"><div class="compare-fill now" style="--w:${(next / max) * 100}%"></div></div>
        <span class="compare-amt">${moneyExact(next)}</span>
      </div>
      <div class="compare-row">
        <span class="compare-label">If fixed</span>
        <div class="compare-track"><div class="compare-fill save" style="--w:${(recovered / max) * 100}%"></div></div>
        <span class="compare-amt">${moneyExact(recovered)}</span>
      </div>
    </div>
    <p class="compare-note">
      Projection uses a dampened MoM (${pct(forecast.assumption_mom_ratio)}).
      “If fixed” subtracts addressable opportunity from the next invoice.
    </p>`;
}

function renderGovernance(gov) {
  if (!gov) return;
  document.getElementById("gov-cadence").textContent = gov.cadence || "";
  document.getElementById("gov-roles").innerHTML = (gov.roles || [])
    .map(
      (r) => `
      <div class="gov-role">
        <strong>${r.role}</strong>
        <span>${r.owns}</span>
      </div>`
    )
    .join("");
  document.getElementById("gov-verify").textContent = gov.verify || "";
}

function wireMessages(messages) {
  document.querySelectorAll("[data-msg]").forEach((node) => {
    const key = node.getAttribute("data-msg");
    const payload = messages?.[key];
    if (payload?.message) node.textContent = payload.message;
  });
}

function revealOnScroll() {
  const nodes = document.querySelectorAll("[data-reveal]");
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.18 }
  );
  nodes.forEach((n) => io.observe(n));
}

async function main() {
  const res = await fetch("./data/snapshot.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`snapshot fetch failed: ${res.status}`);
  const data = await res.json();

  renderHeroChart(document.getElementById("hero-chart"), data.top_services || []);
  renderOutcomeStrip(document.getElementById("outcome-strip"), data);
  wireMessages(data.messages);
  renderMetrics(document.getElementById("metric-strip"), data);
  renderSpendCompare(document.getElementById("spend-compare"), data);
  renderDrivers(document.getElementById("driver-chart"), data.top_services || []);
  renderTrendList(
    document.getElementById("trend-risers"),
    data.risers || [],
    "No risers in this snapshot."
  );
  renderTrendList(
    document.getElementById("trend-fallers"),
    data.fallers || [],
    "No fallers in this snapshot."
  );
  renderPareto(
    document.getElementById("pareto-strip"),
    document.getElementById("pareto-chart"),
    data.pareto
  );
  renderSavings(
    document.getElementById("savings-strip"),
    document.getElementById("savings-list"),
    data.savings
  );
  document.getElementById("opportunity-total").textContent = `${money(
    data.opportunity_total_usd
  )} addressable this period`;
  renderOpportunities(
    document.getElementById("opp-breakdown"),
    document.getElementById("opp-list"),
    data.actions || [],
    data.opportunity_total_usd
  );
  renderQueue(document.getElementById("action-queue"), data.actions || []);
  renderAllocation(
    document.getElementById("alloc-strip"),
    document.getElementById("alloc-gaps"),
    data.allocation
  );
  renderForecast(
    document.getElementById("forecast-strip"),
    document.getElementById("forecast-compare"),
    data.forecast,
    data.invoice_total_usd
  );
  renderAlerts(document.getElementById("alert-row"), data.alerts || {});
  renderGovernance(data.governance);
  document.getElementById("disclaimer").textContent =
    `${data.period_label || ""} · ${data.disclaimer || ""} · ${data.version || ""}`.trim();

  revealOnScroll();
}

main().catch((err) => {
  console.error(err);
  document.querySelectorAll(".section-msg").forEach((n) => {
    if (!n.textContent || n.textContent.includes("Loading")) {
      n.textContent = "Could not load demo snapshot. Regenerate with inject-csv.";
    }
  });
});
