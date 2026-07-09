/* ==========================================================
   RetailIQ — Admin Dashboard interactions
   Loads after admin-main.js (clock, dropdowns, sidebar, logout
   are already wired). This file owns every dashboard widget:
   KPIs, charts, tables, cards, timelines, and the score ring.

   Each render function accepts a data object shaped like the
   payload its matching FastAPI endpoint (see structure.txt)
   is expected to return. loadDashboard() tries the real
   endpoint first and falls back to MOCK_DATA so the page
   always renders something useful during development.
   ========================================================== */

(function () {
  "use strict";

  const CHART_COLORS = {
    indigo: "#4a4ee0",
    indigoSoft: "rgba(74,78,224,0.14)",
    teal: "#2fb6a3",
    tealSoft: "rgba(47,182,163,0.14)",
    yellow: "#c8830f",
    yellowSoft: "rgba(200,131,15,0.14)",
    red: "#c8461e",
    green: "#1fa15a",
    grid: "rgba(38,50,74,0.08)",
    text: "#5b6b85",
  };

  const CATEGORY_COLORS = ["#4a4ee0", "#2fb6a3", "#c8830f", "#c8461e", "#6366f1", "#1fa15a", "#8a6fd8"];

  if (window.Chart) {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = CHART_COLORS.text;
  }

  // -----------------------------------------------------------
  // Mock data — mirrors the shape of each suggested endpoint
  // -----------------------------------------------------------
  const MOCK_DATA = {
    summary: {
      revenue_today: 125480, revenue_change: 8.4,
      orders_today: 486, orders_change: 4.1,
      active_customers: 352, customers_change: 2.6,
      products_sold_today: 2145, products_change: -1.2,
      inventory_health: 92, shelf_occupancy: 96,
    },

    sales: {
      today: {
        labels: ["6am", "8am", "10am", "12pm", "2pm", "4pm", "6pm", "8pm", "10pm"],
        revenue: [2100, 5400, 9800, 15200, 13100, 17600, 21400, 24800, 16080],
        orders: [8, 19, 34, 52, 47, 61, 74, 88, 63],
        profit: [600, 1500, 2900, 4600, 3900, 5300, 6500, 7600, 4900],
      },
      "7d": {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        revenue: [98200, 102400, 96800, 111500, 128900, 145200, 125480],
        orders: [412, 430, 398, 455, 502, 561, 486],
        profit: [29600, 30700, 28100, 33700, 39200, 44100, 37900],
      },
      month: {
        labels: ["Wk 1", "Wk 2", "Wk 3", "Wk 4"],
        revenue: [682000, 715400, 698200, 744900],
        orders: [2980, 3120, 3040, 3260],
        profit: [204600, 214100, 209100, 223700],
      },
      year: {
        labels: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        revenue: [2650000,2480000,2710000,2890000,3010000,3120000,3280000,3190000,3050000,3310000,3480000,3620000],
        orders: [11200,10600,11800,12400,12900,13400,14100,13700,13100,14200,14900,15400],
        profit: [795000,744000,813000,867000,903000,936000,984000,957000,915000,993000,1044000,1086000],
      },
    },

    profit: {
      labels: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct"],
      revenue_actual: [2650000,2480000,2710000,2890000,3010000,3120000,3280000, null, null, null],
      expenses_actual: [1890000,1780000,1920000,2010000,2070000,2110000,2160000, null, null, null],
      net_profit_actual: [760000,700000,790000,880000,940000,1010000,1120000, null, null, null],
      net_profit_forecast: [null, null, null, null, null, null, 1120000, 1205000, 1260000, 1340000],
    },

    categories: [
      { name: "Dairy", sales: 5240, revenue: 312400, pct: 24 },
      { name: "Bakery", sales: 3810, revenue: 198200, pct: 16 },
      { name: "Drinks", sales: 4620, revenue: 226800, pct: 18 },
      { name: "Snacks", sales: 3110, revenue: 154600, pct: 12 },
      { name: "Vegetables", sales: 2890, revenue: 121300, pct: 10 },
      { name: "Fruits", sales: 2470, revenue: 108900, pct: 9 },
      { name: "Frozen Foods", sales: 1980, revenue: 96500, pct: 8 },
    ],

    topProducts: [
      { name: "Organic Milk 1L", category: "Dairy", icon: "🥛", units: 1240, revenue: 62000, stock: 380 },
      { name: "Sourdough Bakery Loaf", category: "Bakery", icon: "🍞", units: 980, revenue: 44100, stock: 22 },
      { name: "Sparkling Water 6-Pack", category: "Drinks", icon: "🥤", units: 870, revenue: 52200, stock: 145 },
      { name: "Salted Pretzel Bites", category: "Snacks", icon: "🥨", units: 760, revenue: 22800, stock: 8 },
      { name: "Cherry Tomatoes 500g", category: "Vegetables", icon: "🍅", units: 640, revenue: 19200, stock: 96 },
      { name: "Frozen Mixed Berries", category: "Frozen Foods", icon: "🍓", units: 590, revenue: 26550, stock: 0 },
    ],

    inventory: {
      total_products: 1284, available_products: 1142, out_of_stock: 18,
      low_stock: 37, new_products: 12, hidden_products: 6,
      distribution: {
        labels: ["Dairy","Bakery","Drinks","Snacks","Vegetables","Fruits","Frozen Foods"],
        values: [268, 194, 231, 176, 158, 132, 125],
      },
    },

    lowStock: [
      { name: "Whole Milk 1L", remaining: 8, minimum: 30, location: "Aisle 1 · Shelf B", priority: "high" },
      { name: "Sourdough Bakery Loaf", remaining: 22, minimum: 40, location: "Aisle 2 · Shelf A", priority: "medium" },
      { name: "Salted Pretzel Bites", remaining: 8, minimum: 25, location: "Aisle 4 · Shelf C", priority: "high" },
      { name: "Sparkling Water 6-Pack", remaining: 34, minimum: 50, location: "Aisle 3 · Shelf D", priority: "low" },
    ],

    offers: [
      { name: "Sparkling Water 6-Pack", icon: "🥤", discount: "20% OFF", days_remaining: 3, sales_during_promo: 870 },
      { name: "Sourdough Bakery Loaf", icon: "🍞", discount: "15% OFF", days_remaining: 5, sales_during_promo: 640 },
      { name: "Cherry Tomatoes 500g", icon: "🍅", discount: "10% OFF", days_remaining: 2, sales_during_promo: 410 },
      { name: "Frozen Mixed Berries", icon: "🍓", discount: "25% OFF", days_remaining: 6, sales_during_promo: 355 },
    ],

    customers: {
      total_registered: 4920, returning: 2610, new: 318, avg_basket: 258,
      segments: { labels: ["Regular", "New", "VIP", "Churn Risk"], values: [46, 22, 18, 14] },
    },

    insights: [
      { icon: "📈", text: "Beverage sales increased by 15% this week." },
      { icon: "🥛", text: "Dairy inventory will require restocking within two days." },
      { icon: "📅", text: "Weekend demand is expected to increase." },
      { icon: "🍞", text: "Bakery promotions generated 22% additional revenue." },
      { icon: "🔁", text: "Returning customers spend 35% more than new customers." },
      { icon: "🧊", text: "Frozen foods category is trending down 4% month-over-month." },
    ],

    forecast: {
      sales: {
        labels: ["-6d","-5d","-4d","-3d","-2d","-1d","Today","+1d","+2d","+3d","+4d","+5d","+6d","+7d"],
        actual: [118000,121400,109800,132600,128900,140200,125480, null, null, null, null, null, null, null],
        predicted: [null, null, null, null, null, null, 125480, 145000, 138200, 151600, 149400, 162800, 158100, 167300],
      },
      demand: {
        labels: ["+1d","+2d","+3d","+4d","+5d","+6d","+7d"],
        milk: [18, 14, 21, 17, 24, 19, 22],
      },
      profit_prediction: 52000,
      restock_recommendation: ["Rice", "Sugar", "Milk"],
    },

    orders: [
      { id: "#RTQ-10482", customer: "Youssef Adel", products: "Milk, Bread, Eggs", total: 342, payment: "Card", status: "Delivered" },
      { id: "#RTQ-10481", customer: "Mona Farouk", products: "Sparkling Water x6", total: 186, payment: "Cash", status: "Processing" },
      { id: "#RTQ-10480", customer: "Karim Said", products: "Frozen Berries, Yogurt", total: 214, payment: "Card", status: "Delivered" },
      { id: "#RTQ-10479", customer: "Nour Hassan", products: "Rice 5kg, Sugar 2kg", total: 298, payment: "Wallet", status: "Cancelled" },
      { id: "#RTQ-10478", customer: "Amr Tarek", products: "Pretzels, Soda x2", total: 122, payment: "Cash", status: "Delivered" },
    ],

    system: [
      { name: "Database", color: "green", status: "Operational", sync: "Synced 1 min ago" },
      { name: "AI Services", color: "green", status: "Operational", sync: "Synced 2 min ago" },
      { name: "Detection Model", color: "green", status: "Operational", sync: "Synced 4 min ago" },
      { name: "Forecast Engine", color: "yellow", status: "Degraded — job retrying", sync: "Synced 12 min ago" },
      { name: "Mail Service", color: "green", status: "Operational", sync: "Synced 3 min ago" },
      { name: "Server Status", color: "green", status: "Operational", sync: "Synced 1 min ago" },
    ],

    activity: [
      { icon: "📦", text: "Updated inventory for Dairy category", time: "Today, 9:12 AM" },
      { icon: "📄", text: "Generated monthly business report", time: "Today, 8:30 AM" },
      { icon: "📷", text: "Completed shelf scan — Aisle 3", time: "Yesterday, 5:47 PM" },
      { icon: "🆕", text: "Added new product: Sourdough Bakery Loaf", time: "Yesterday, 3:20 PM" },
      { icon: "🏷️", text: "Created offer: Sparkling Water 6-Pack", time: "2 days ago" },
      { icon: "🗂️", text: "Updated category: Snacks", time: "3 days ago" },
    ],

    performance_score: {
      score: 92,
      explanation: "Excellent inventory health with strong customer engagement. Focus on replenishing dairy products and extending current beverage promotions.",
    },
  };

  // -----------------------------------------------------------
  // Fetch helper — tries the real API, falls back to mock data
  // -----------------------------------------------------------
  async function loadWidget(endpoint, mockKey) {
    try {
      const res = await fetch(endpoint, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("bad response");
      return await res.json();
    } catch (err) {
      return MOCK_DATA[mockKey];
    }
  }

  function money(n) {
    return "EGP " + Number(n).toLocaleString("en-US", { maximumFractionDigits: 0 });
  }

  // -----------------------------------------------------------
  // KPI cards
  // -----------------------------------------------------------
  function renderSummary(data) {
    const el = (id) => document.getElementById(id);
    el("kpiRevenue").textContent = Number(data.revenue_today).toLocaleString("en-US") + " EGP";
    el("kpiRevenueTrend").textContent = (data.revenue_change >= 0 ? "▲ +" : "▼ ") + data.revenue_change + "%";
    el("kpiRevenueTrend").className = "kpi-trend " + (data.revenue_change >= 0 ? "trend-up" : "trend-down");

    el("kpiOrders").textContent = data.orders_today;
    el("kpiOrdersTrend").textContent = (data.orders_change >= 0 ? "▲ +" : "▼ ") + data.orders_change + "%";
    el("kpiOrdersTrend").className = "kpi-trend " + (data.orders_change >= 0 ? "trend-up" : "trend-down");

    el("kpiCustomers").textContent = data.active_customers;
    el("kpiCustomersTrend").textContent = (data.customers_change >= 0 ? "▲ +" : "▼ ") + data.customers_change + "%";
    el("kpiCustomersTrend").className = "kpi-trend " + (data.customers_change >= 0 ? "trend-up" : "trend-down");

    el("kpiProductsSold").textContent = Number(data.products_sold_today).toLocaleString("en-US");
    el("kpiProductsTrend").textContent = (data.products_change >= 0 ? "▲ +" : "▼ ") + data.products_change + "%";
    el("kpiProductsTrend").className = "kpi-trend " + (data.products_change >= 0 ? "trend-up" : "trend-down");

    el("kpiInventoryHealth").textContent = data.inventory_health + "%";
    el("kpiShelfOccupancy").textContent = data.shelf_occupancy + "%";
  }

  // -----------------------------------------------------------
  // Sales performance chart (with range tabs)
  // -----------------------------------------------------------
  let salesChart = null;

  function buildSalesChart(rangeData) {
    const ctx = document.getElementById("salesPerformanceChart");
    if (!ctx || !window.Chart) return;

    const config = {
      type: "line",
      data: {
        labels: rangeData.labels,
        datasets: [
          {
            label: "Revenue",
            data: rangeData.revenue,
            borderColor: CHART_COLORS.indigo,
            backgroundColor: CHART_COLORS.indigoSoft,
            fill: true,
            tension: 0.35,
            yAxisID: "y",
          },
          {
            label: "Orders",
            data: rangeData.orders,
            borderColor: CHART_COLORS.teal,
            backgroundColor: CHART_COLORS.tealSoft,
            fill: false,
            tension: 0.35,
            yAxisID: "y1",
          },
          {
            label: "Profit",
            data: rangeData.profit,
            borderColor: CHART_COLORS.yellow,
            backgroundColor: CHART_COLORS.yellowSoft,
            fill: false,
            tension: 0.35,
            yAxisID: "y",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#10182a",
            padding: 12,
            titleFont: { family: "'Space Grotesk', sans-serif", weight: "600" },
            bodyFont: { family: "'IBM Plex Mono', monospace", size: 12 },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: { position: "left", grid: { color: CHART_COLORS.grid }, ticks: { callback: (v) => (v / 1000) + "k" } },
          y1: { position: "right", grid: { display: false } },
        },
      },
    };

    if (salesChart) {
      salesChart.data = config.data;
      salesChart.update();
    } else {
      salesChart = new Chart(ctx, config);
    }
  }

  function setupSalesTabs(salesData) {
    // Tabs are kept visible for layout/design purposes, but the chart is
    // now static: clicking a tab only updates which one looks "active" —
    // it no longer swaps the plotted data. The chart always shows the
    // "today" slice.
    const tabs = document.querySelectorAll("#salesRangeTabs .chart-tab");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("is-active"));
        tab.classList.add("is-active");
      });
    });
    buildSalesChart(salesData.today);
  }

  // -----------------------------------------------------------
  // Profit analytics (area + bar combo)
  // -----------------------------------------------------------
  function buildProfitChart(data) {
    const ctx = document.getElementById("profitAnalyticsChart");
    if (!ctx || !window.Chart) return;

    new Chart(ctx, {
      data: {
        labels: data.labels,
        datasets: [
          {
            type: "bar",
            label: "Expenses",
            data: data.expenses_actual,
            backgroundColor: "rgba(200,70,30,0.35)",
            borderRadius: 6,
            order: 3,
          },
          {
            type: "line",
            label: "Revenue",
            data: data.revenue_actual,
            borderColor: CHART_COLORS.indigo,
            backgroundColor: CHART_COLORS.indigoSoft,
            fill: true,
            tension: 0.35,
            spanGaps: false,
            order: 2,
          },
          {
            type: "line",
            label: "Net Profit (actual)",
            data: data.net_profit_actual,
            borderColor: CHART_COLORS.green,
            backgroundColor: "rgba(31,161,90,0.12)",
            fill: true,
            tension: 0.35,
            spanGaps: false,
            pointRadius: 3,
            order: 1,
          },
          {
            type: "line",
            label: "Net Profit (forecast)",
            data: data.net_profit_forecast,
            borderColor: CHART_COLORS.green,
            backgroundColor: "transparent",
            borderDash: [6, 5],
            tension: 0.35,
            spanGaps: true,
            pointRadius: 3,
            order: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true } },
          tooltip: { backgroundColor: "#10182a", padding: 12 },
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: CHART_COLORS.grid }, ticks: { callback: (v) => (v / 1000) + "k" } },
        },
      },
    });
  }

  // -----------------------------------------------------------
  // Sales by category (bar) + legend list
  // -----------------------------------------------------------
  function buildCategoryChart(categories) {
    const ctx = document.getElementById("categoryPieChart");
    if (ctx && window.Chart) {
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: categories.map((c) => c.name),
          datasets: [{
            label: "Share of sales",
            data: categories.map((c) => c.pct),
            backgroundColor: CATEGORY_COLORS,
            borderRadius: 8,
            maxBarThickness: 46,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: "#10182a", padding: 10, callbacks: { label: (c) => `${c.label}: ${c.parsed.y}%` } },
          },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: CHART_COLORS.grid }, ticks: { callback: (v) => v + "%" } },
          },
        },
      });
    }

    const list = document.getElementById("categoryLegendList");
    if (list) {
      list.innerHTML = categories.map((c, i) => `
        <div class="category-legend-row">
          <span class="cat-dot" style="background:${CATEGORY_COLORS[i % CATEGORY_COLORS.length]}"></span>
          <span class="cat-name">${c.name}</span>
          <div class="cat-figures">
            <span class="cat-revenue">${money(c.revenue)} · ${c.sales.toLocaleString("en-US")} sold</span>
            <span class="cat-pct">${c.pct}%</span>
          </div>
        </div>
      `).join("");
    }
  }

  // -----------------------------------------------------------
  // Best selling products table
  // -----------------------------------------------------------
  function renderBestSellers(products) {
    const body = document.getElementById("bestSellersBody");
    if (!body) return;
    const sorted = [...products].sort((a, b) => b.units - a.units);
    body.innerHTML = sorted.map((p) => {
      let stockClass = "stock-ok";
      if (p.stock === 0) stockClass = "stock-out";
      else if (p.stock < 30) stockClass = "stock-low";
      return `
        <tr>
          <td><div class="product-thumb">${p.icon}</div></td>
          <td class="product-name">${p.name}</td>
          <td>${p.category}</td>
          <td>${p.units.toLocaleString("en-US")}</td>
          <td>${money(p.revenue)}</td>
          <td><span class="stock-badge ${stockClass}">${p.stock === 0 ? "Out of stock" : p.stock + " left"}</span></td>
        </tr>
      `;
    }).join("");
  }

  // -----------------------------------------------------------
  // Inventory overview + distribution chart
  // -----------------------------------------------------------
  function renderInventory(inv) {
    const el = (id) => document.getElementById(id);
    el("invTotal").textContent = inv.total_products.toLocaleString("en-US");
    el("invAvailable").textContent = inv.available_products.toLocaleString("en-US");
    el("invOutOfStock").textContent = inv.out_of_stock;
    el("invLowStock").textContent = inv.low_stock;
    el("invNew").textContent = inv.new_products;
    el("invHidden").textContent = inv.hidden_products;

    const ctx = document.getElementById("inventoryDistributionChart");
    if (ctx && window.Chart) {
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: inv.distribution.labels,
          datasets: [{
            label: "Products",
            data: inv.distribution.values,
            backgroundColor: CHART_COLORS.indigo,
            borderRadius: 8,
            maxBarThickness: 46,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { backgroundColor: "#10182a", padding: 10 } },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: CHART_COLORS.grid } },
          },
        },
      });
    }
  }

  // -----------------------------------------------------------
  // Low stock alert cards
  // -----------------------------------------------------------
  function renderLowStock(items) {
    const grid = document.getElementById("lowStockGrid");
    if (!grid) return;
    grid.innerHTML = items.map((item) => `
      <div class="low-stock-card priority-${item.priority}">
        <div class="low-stock-head">
          <span class="low-stock-name">${item.name}</span>
          <span class="priority-tag priority-${item.priority}">${item.priority}</span>
        </div>
        <span class="low-stock-location">${item.location}</span>
        <span class="low-stock-meta"><strong>${item.remaining}</strong> remaining · min <strong>${item.minimum}</strong></span>
        <button class="restock-btn" type="button" data-product="${item.name}">Restock</button>
      </div>
    `).join("");
  }

  // -----------------------------------------------------------
  // Active offers cards
  // -----------------------------------------------------------
  function renderOffers(offers) {
    const grid = document.getElementById("offersGrid");
    if (!grid) return;
    grid.innerHTML = offers.map((o) => `
      <div class="offer-card">
        <div class="offer-card-image">${o.icon}</div>
        <div class="offer-card-body">
          <span class="offer-discount-badge">${o.discount}</span>
          <span class="offer-name">${o.name}</span>
          <div class="offer-meta-row">
            <span>${o.days_remaining} day${o.days_remaining === 1 ? "" : "s"} left</span>
            <span><strong>${o.sales_during_promo}</strong> sold</span>
          </div>
        </div>
      </div>
    `).join("");
  }

  // -----------------------------------------------------------
  // Customer segments chart
  // -----------------------------------------------------------
  function renderCustomerSegments(segments) {
    const ctx = document.getElementById("customerSegmentsChart");
    if (ctx && window.Chart) {
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: segments.labels,
          datasets: [{
            data: segments.values,
            backgroundColor: [CHART_COLORS.indigo, CHART_COLORS.teal, CHART_COLORS.yellow, CHART_COLORS.red],
            borderWidth: 2,
            borderColor: "#ffffff",
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: "#10182a", padding: 10, callbacks: { label: (c) => `${c.label}: ${c.parsed}%` } },
          },
        },
      });
    }

    const colors = [CHART_COLORS.indigo, CHART_COLORS.teal, CHART_COLORS.yellow, CHART_COLORS.red];
    const list = document.getElementById("segmentsLegendList");
    if (list) {
      list.innerHTML = segments.labels.map((label, i) => `
        <div class="category-legend-row">
          <span class="cat-dot" style="background:${colors[i]}"></span>
          <span class="cat-name">${label}</span>
          <div class="cat-figures"><span class="cat-pct">${segments.values[i]}%</span></div>
        </div>
      `).join("");
    }
  }

  // -----------------------------------------------------------
  // AI business insights
  // -----------------------------------------------------------
  function renderInsights(insights) {
    const grid = document.getElementById("insightsGrid");
    if (!grid) return;
    grid.innerHTML = insights.map((i) => `
      <div class="insight-card">
        <div class="insight-icon">${i.icon}</div>
        <p class="insight-text">${i.text}</p>
      </div>
    `).join("");
  }

  // -----------------------------------------------------------
  // Forecast charts (sales: actual solid / predicted dashed,
  // demand: bar per upcoming day)
  // -----------------------------------------------------------
  function buildForecastCharts(forecast) {
    const salesCtx = document.getElementById("salesForecastChart");
    if (salesCtx && window.Chart) {
      new Chart(salesCtx, {
        type: "line",
        data: {
          labels: forecast.sales.labels,
          datasets: [
            {
              label: "Actual",
              data: forecast.sales.actual,
              borderColor: CHART_COLORS.indigo,
              backgroundColor: "transparent",
              spanGaps: false,
              tension: 0.3,
              pointRadius: 3,
            },
            {
              label: "Predicted",
              data: forecast.sales.predicted,
              borderColor: CHART_COLORS.teal,
              backgroundColor: "transparent",
              borderDash: [6, 5],
              spanGaps: true,
              tension: 0.3,
              pointRadius: 3,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: "bottom", labels: { boxWidth: 10, boxHeight: 10, usePointStyle: true } },
            tooltip: { backgroundColor: "#10182a", padding: 10 },
          },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: CHART_COLORS.grid }, ticks: { callback: (v) => (v / 1000) + "k" } },
          },
        },
      });
    }

    const demandCtx = document.getElementById("demandForecastChart");
    if (demandCtx && window.Chart) {
      new Chart(demandCtx, {
        type: "bar",
        data: {
          labels: forecast.demand.labels,
          datasets: [{
            label: "Milk demand change (%)",
            data: forecast.demand.milk,
            backgroundColor: forecast.demand.milk.map((v) => (v >= 18 ? CHART_COLORS.green : CHART_COLORS.teal)),
            borderRadius: 8,
            maxBarThickness: 40,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: "#10182a", padding: 10, callbacks: { label: (c) => `+${c.parsed.y}% demand` } },
          },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: CHART_COLORS.grid }, ticks: { callback: (v) => "+" + v + "%" } },
          },
        },
      });
    }

    const tomorrow = document.getElementById("forecastTomorrowValue");
    if (tomorrow) tomorrow.textContent = money(forecast.sales.predicted.find((v) => v !== null && forecast.sales.actual[forecast.sales.predicted.indexOf(v)] === undefined) || 145000);
  }

  // -----------------------------------------------------------
  // Recent orders table
  // -----------------------------------------------------------
  function renderOrders(orders) {
    const body = document.getElementById("recentOrdersBody");
    if (!body) return;
    const statusClass = { Delivered: "status-delivered", Processing: "status-processing", Cancelled: "status-cancelled" };
    body.innerHTML = orders.map((o) => `
      <tr>
        <td><strong>${o.id}</strong></td>
        <td>${o.customer}</td>
        <td>${o.products}</td>
        <td>${money(o.total)}</td>
        <td>${o.payment}</td>
        <td><span class="order-status-badge ${statusClass[o.status] || ""}">${o.status}</span></td>
        <td><button class="table-view-btn" type="button" data-order="${o.id}">View Details</button></td>
      </tr>
    `).join("");
  }

  // -----------------------------------------------------------
  // System health grid
  // -----------------------------------------------------------
  function renderSystemHealth(systems) {
    const grid = document.getElementById("systemHealthGrid");
    if (!grid) return;
    grid.innerHTML = systems.map((s) => `
      <div class="health-card">
        <span class="health-dot dot-${s.color}"></span>
        <div class="health-body">
          <span class="health-name">${s.name}</span>
          <span class="health-status">${s.status}</span>
          <span class="health-sync">${s.sync}</span>
        </div>
      </div>
    `).join("");
  }

  // -----------------------------------------------------------
  // Recent administrative activity timeline
  // -----------------------------------------------------------
  function renderActivity(items) {
    const timeline = document.getElementById("activityTimeline");
    if (!timeline) return;
    timeline.innerHTML = items.map((a) => `
      <div class="activity-item">
        <div class="activity-icon">${a.icon}</div>
        <div class="activity-content">
          <p class="activity-text">${a.text}</p>
          <span class="activity-time">${a.time}</span>
        </div>
      </div>
    `).join("");
  }

  // -----------------------------------------------------------
  // Business performance score ring
  // -----------------------------------------------------------
  function renderPerformanceScore(perf) {
    const valueEl = document.getElementById("performanceScoreValue");
    const explanationEl = document.getElementById("scoreExplanation");
    const ringFg = document.getElementById("scoreRingFg");
    if (valueEl) valueEl.textContent = perf.score;
    if (explanationEl) explanationEl.textContent = perf.explanation;
    if (ringFg) {
      const circumference = 2 * Math.PI * 52;
      const offset = circumference - (perf.score / 100) * circumference;
      ringFg.style.strokeDasharray = circumference.toFixed(1);
      ringFg.style.strokeDashoffset = offset.toFixed(1);
    }
  }

  // -----------------------------------------------------------
  // Restock buttons (delegated) — placeholder POST to backend
  // -----------------------------------------------------------
  document.addEventListener("click", (e) => {
    const btn = e.target.closest(".restock-btn");
    if (!btn) return;
    const product = btn.getAttribute("data-product");
    btn.textContent = "Requested ✓";
    btn.disabled = true;
    fetch("/admin/dashboard/low-stock/restock", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product }),
    }).catch(() => {});
  });

  // -----------------------------------------------------------
  // Boot
  // -----------------------------------------------------------

  // Every value here maps a "section" to:
  //  - the key that section lives under in the /admin/overview payload
  //  - the key it falls back to in MOCK_DATA when the backend hasn't
  //    shipped that section yet (or a single field is missing/empty)
  // This lets each widget go live independently as the backend fills in
  // more of the payload, instead of an all-or-nothing switch.
  function pick(data, dataKey, mockKey) {
    const value = data ? data[dataKey] : undefined;
    const isEmpty =
      value === undefined ||
      value === null ||
      (Array.isArray(value) && value.length === 0) ||
      (typeof value === "object" && !Array.isArray(value) && Object.keys(value).length === 0);
    return isEmpty ? MOCK_DATA[mockKey] : value;
  }

  // Wrap each render call so one bad/missing section can't stop the
  // rest of the dashboard from rendering.
  function safeRender(label, fn) {
    try {
      fn();
    } catch (err) {
      console.warn(`Dashboard section "${label}" failed to render:`, err);
    }
  }

  async function loadDashboard() {
    showGlobalLoader();

    // Charts/widgets are static: no backend call is made, every section
    // always renders from the hardcoded MOCK_DATA below via pick().
    const data = {};

    // KPIs
    safeRender("summary", () => renderSummary(pick(data, "operational_summary", "summary")));

    // Sales performance (line chart + range tabs) — all ranges arrive
    // in one payload, tabs just switch which slice is plotted.
    safeRender("sales", () => setupSalesTabs(pick(data, "sales_performance", "sales")));

    // Profit analytics (bar + line combo)
    safeRender("profit", () => buildProfitChart(pick(data, "profit_analytics", "profit")));

    // Sales by category (donut + legend)
    safeRender("categories", () => buildCategoryChart(pick(data, "categories", "categories")));

    // Best selling products table
    safeRender("topProducts", () => renderBestSellers(pick(data, "top_products", "topProducts")));

    // Inventory overview (summary cards + distribution chart)
    safeRender("inventory", () => renderInventory(pick(data, "inventory", "inventory")));

    // Low stock alert cards
    safeRender("lowStock", () => renderLowStock(pick(data, "low_stock", "lowStock")));

    // Active offers cards
    safeRender("offers", () => renderOffers(pick(data, "offers", "offers")));

    // Customer analytics (segments donut + legend)
    safeRender("customers", () => {
      const customers = pick(data, "customer_analytics", "customers");
      renderCustomerSegments(customers.segments);
    });

    // AI business insights
    safeRender("insights", () => renderInsights(pick(data, "insights", "insights")));

    // Forecast summary (sales forecast + demand forecast charts)
    safeRender("forecast", () => buildForecastCharts(pick(data, "forecast", "forecast")));

    // Recent orders table
    safeRender("orders", () => renderOrders(pick(data, "recent_orders", "orders")));

    // System health grid
    safeRender("systemHealth", () => renderSystemHealth(pick(data, "system_health", "system")));

    // Recent administrative activity timeline
    safeRender("activity", () => renderActivity(pick(data, "activity", "activity")));

    // Business performance score ring
    safeRender("performanceScore", () => renderPerformanceScore(pick(data, "performance_score", "performance_score")));

    hideGlobalLoader();
  }

  document.addEventListener("DOMContentLoaded", loadDashboard);
})();