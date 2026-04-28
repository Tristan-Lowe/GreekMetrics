// static/charts.js

// ── Slider live-update ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('input[type="range"].gm-slider').forEach(function (slider) {
    const display = document.getElementById(slider.id + '_display');
    if (display) display.textContent = slider.value;
    slider.addEventListener('input', function () {
      if (display) display.textContent = this.value;
    });
  });
});

// ── Chart.js helpers ────────────────────────────────────────────────────────
function renderBarChart(canvasId, labels, data, colors) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#252b3b' }, ticks: { color: '#8892a4', font: { size: 11 } } },
        y: { grid: { color: '#252b3b' }, ticks: { color: '#8892a4', font: { size: 11 } }, min: 0 }
      }
    }
  });
}

function renderLineChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        borderColor: '#7c8cf8',
        backgroundColor: 'rgba(124,140,248,0.1)',
        borderWidth: 2,
        pointBackgroundColor: '#7c8cf8',
        fill: true,
        tension: 0.3,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: '#252b3b' }, ticks: { color: '#8892a4', font: { size: 10 } } },
        y: { grid: { color: '#252b3b' }, ticks: { color: '#8892a4', font: { size: 10 } }, min: 0, max: 100 }
      }
    }
  });
}
