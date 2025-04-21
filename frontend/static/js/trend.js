// один общий тултип для всех точек и баров
const tooltip = d3.select("body")
  .append("div")
    .attr("class", "d3-tooltip")
    .style("position", "absolute")
    .style("pointer-events", "none")
    .style("padding", "6px 10px")
    .style("background", "rgba(0,0,0,0.7)")
    .style("color", "#fff")
    .style("border-radius", "4px")
    .style("font-size", "12px")
    .style("opacity", 0);

const TrendPage = {
  raw: [],   // сюда запомним необработанные данные

  init() {
    this.setDefaultDates();
    document.getElementById('apply-trend')
      .addEventListener('click', () => this.applyFilters());
    // при первой загрузке — подгружаем всё и прорисовываем
    this.applyFilters();
  },

  setDefaultDates() {
    const today = new Date(),
          monthAgo = new Date();
    monthAgo.setMonth(monthAgo.getMonth() - 1);
    document.getElementById('trend-end').value   = today.toISOString().slice(0,10);
    document.getElementById('trend-start').value = monthAgo.toISOString().slice(0,10);
  },

  applyFilters() {
    // Собираем значения фильтров
    const from = document.getElementById('trend-start').value;
    const to   = document.getElementById('trend-end').value;
    const sev  = document.getElementById('trend-severity').value;
    const att  = document.getElementById('trend-attack').value;

    // Запрашиваем "сырые" данные (API без фильтрации)
    // (или можно передавать params прямо в API, если сервер поддерживает)
    fetch('/api/vulnerabilities')
      .then(r => r.json())
      .then(json => {
        // сохраняем raw для последующей фильтрации
        this.raw = json.vulnerabilities.map(v => ({
          date: v.published_date.split('T')[0],
          cvss_score: v.cvss_v3?.base_score ?? v.cvss_v2?.base_score ?? 0,
          severity:   v.cvss_v3?.severity     || v.cvss_v2?.severity     || 'UNKNOWN',
          attack_vector: v.cvss_v3?.attack_vector || v.cvss_v2?.access_vector || 'UNKNOWN'
        }));

        // фильтруем по датам, severity и attack vector
        let filtered = this.raw.filter(d => {
          if (from && d.date < from) return false;
          if (to   && d.date > to)   return false;
          if (sev !== 'all' && d.severity !== sev) return false;
          if (att !== 'all' && d.attack_vector !== att) return false;
          return true;
        });

        // группируем по дате и считаем количество
        const grouped = Array.from(
          d3.rollup(filtered, vs => vs.length, d => d.date),
          ([date, cnt]) => ({ date: new Date(date), cnt })
        ).sort((a,b) => a.date - b.date);

        this.renderChart(grouped);
      });
  },

  renderChart(data) {
    const sel = '#trend-chart';
    const container = d3.select(sel).node().parentNode;
    const { width, height } = container.getBoundingClientRect();
    const margin = { top:20, right:20, bottom:60, left:50 };
    const W = width - margin.left - margin.right;
    const H = height - margin.top - margin.bottom;

    // очищаем старое
    d3.select(sel).selectAll('*').remove();

    const svg = d3.select(sel)
      .append('svg')
        .attr('width',  width)
        .attr('height', height)
      .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // шкалы
    const x = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, W]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.cnt)]).nice()
      .range([H, 0]);

    // ось X
    svg.append('g')
      .attr('transform', `translate(0,${H})`)
      .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat('%d %b')))
      .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end');

    // ось Y
    svg.append('g')
      .call(d3.axisLeft(y).ticks(5));

    // линия с анимацией
    const line = d3.line()
      .curve(d3.curveMonotoneX)
      .x(d => x(d.date))
      .y(d => y(d.cnt));

    const path = svg.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', 'var(--accent-from)')
      .attr('stroke-width', 2)
      .attr('d', line);

    // анимируем появление линии
    const totalLen = path.node().getTotalLength();
    path
      .attr('stroke-dasharray', `0,${totalLen}`)
      .transition().duration(800)
        .attrTween('stroke-dasharray', () => t => `${t * totalLen},${totalLen}`);

    // точки и тултипы
    svg.selectAll('circle')
      .data(data)
      .join('circle')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.cnt))
        .attr('r', 4)
        .attr('fill', 'var(--accent-to)')
        .on('mouseover', (e, d) => {
          tooltip.html(
            `${d3.timeFormat('%Y-%m-%d')(d.date)}<br><strong>New: ${d.cnt}</strong>`
          )
          .style('left',  e.pageX + 10 + 'px')
          .style('top',   e.pageY + 10 + 'px')
          .transition().style('opacity', 1);
        })
        .on('mousemove', e => {
          tooltip
            .style('left', e.pageX + 10 + 'px')
            .style('top',  e.pageY + 10 + 'px');
        })
        .on('mouseout', () => {
          tooltip.transition().style('opacity', 0);
        });
  }
};

document.addEventListener('DOMContentLoaded', () => TrendPage.init());
