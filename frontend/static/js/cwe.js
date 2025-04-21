// тултип (общий)
const tooltip = d3.select("body")
  .append("div")
    .attr("class", "d3-tooltip");

const CWEPage = {
  cwe: null,
  data: [],

  init() {
    this.cwe = new URLSearchParams(window.location.search).get('cwe') || '';
    document.getElementById('cwe-filter').value = this.cwe;
    document.getElementById('apply-cwe')
      .addEventListener('click', ()=>this.onApply());
    // если параметр в URL — применяем сразу
    if (this.cwe) this.loadData();
  },

  onApply() {
    this.cwe = document.getElementById('cwe-filter').value.trim();
    if (!this.cwe) return alert('Введите CWE, например CWE-79');
    // меняем URL
    const url = `${window.location.pathname}?cwe=${encodeURIComponent(this.cwe)}`;
    history.pushState(null,'', url);
    this.loadData();
  },

  loadData() {
    document.getElementById('cwe-title').textContent = this.cwe;
    fetch(`/api/vulnerabilities?cwe=${encodeURIComponent(this.cwe)}`)
      .then(r=>r.json())
      .then(j=>{
        this.data = j.vulnerabilities.map(v=>({
          cve_id: v.cve_id,
          published_date: v.published_date.split('T')[0],
          cvss_score: v.cvss_v3?.base_score ?? v.cvss_v2?.base_score ?? 0,
          severity: v.cvss_v3?.severity || v.cvss_v2?.severity || 'UNKNOWN',
          vendor: (v.vendor || 'Unknown')
        }));
        this.renderCharts();
        this.renderTable();
      });
  },

  renderTable() {
    const tbody = document.querySelector('#cwe-table tbody');
    tbody.innerHTML = '';
    this.data.forEach(v=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${v.cve_id}</td>
        <td>${v.published_date}</td>
        <td>${v.cvss_score.toFixed(1)}</td>
        <td>${v.severity}</td>
        <td>${v.vendor}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  renderCharts() {
    this.renderScoreDistribution();
    this.renderVendorDistribution();
  },

  renderScoreDistribution() {
    const sel = '#cwe-score-distribution';
    const arr = Array.from(
      d3.rollup(this.data, v=>v.length, d=>Math.floor(d.cvss_score)),
      ([score, cnt]) => ({score, cnt})
    ).sort((a,b)=>a.score-b.score);

    const container = d3.select(sel).node().parentNode;
    const { width, height } = container.getBoundingClientRect();
    const m = {top:20, right:20, bottom:40, left:50};
    const W = width - m.left - m.right;
    const H = height - m.top - m.bottom;

    const svg = d3.select(sel).html('')
      .append('svg').attr('width', width).attr('height', height)
      .append('g').attr('transform',`translate(${m.left},${m.top})`);

    const x = d3.scaleBand(arr.map(d=>d.score), [0,W]).padding(0.2);
    const y = d3.scaleLinear().domain([0, d3.max(arr,d=>d.cnt)]).nice().range([H,0]);

    // оси
    svg.append('g').call(d3.axisLeft(y).ticks(5));
    svg.append('g')
      .attr('transform',`translate(0,${H})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
        .attr('transform','rotate(-45)')
        .style('text-anchor','end');

    // бары
    svg.selectAll('rect')
      .data(arr).join('rect')
      .attr('x', d=>x(d.score))
      .attr('y', H)
      .attr('width', x.bandwidth())
      .attr('height', 0)
      .attr('fill', 'var(--accent-from)')
      .on("mouseover",(e,d)=>{
        tooltip.html(`Score ${d.score}: ${d.cnt}`)
          .style("left", e.pageX+10+"px")
          .style("top",  e.pageY+10+"px")
          .transition().style("opacity",1);
      })
      .on("mousemove",e=>{
        tooltip.style("left", e.pageX+10+"px")
               .style("top",  e.pageY+10+"px");
      })
      .on("mouseout",()=>tooltip.transition().style("opacity",0))
      .transition().duration(600)
        .attr('y', d=>y(d.cnt))
        .attr('height', d=>H - y(d.cnt));
  },

  renderVendorDistribution() {
    const sel = '#cwe-vendor-distribution';
    const arr = Array.from(
      d3.rollup(this.data, v=>v.length, d=>d.vendor),
      ([vendor, cnt]) => ({vendor, cnt})
    ).sort((a,b)=>b.cnt-a.cnt).slice(0,10);

    const container = d3.select(sel).node().parentNode;
    const { width, height } = container.getBoundingClientRect();
    const m = {top:20, right:20, bottom:20, left:100};
    const W = width - m.left - m.right;
    const H = height - m.top - m.bottom;

    const svg = d3.select(sel).html('')
      .append('svg').attr('width', width).attr('height', height)
      .append('g').attr('transform',`translate(${m.left},${m.top})`);

    const x = d3.scaleLinear().domain([0,d3.max(arr,d=>d.cnt)]).nice().range([0,W]);
    const y = d3.scaleBand(arr.map(d=>d.vendor), [0,H]).padding(0.2);

    // ось Y
    svg.append('g').call(d3.axisLeft(y)).selectAll('text').style('fill','#ccc');

    // бары
    svg.selectAll('rect')
      .data(arr).join('rect')
      .attr('y', d=>y(d.vendor))
      .attr('height', y.bandwidth())
      .attr('x', 0)
      .attr('width', 0)
      .attr('fill', 'var(--accent-to)')
      .on("mouseover",(e,d)=>{
        tooltip.html(`${d.vendor}: ${d.cnt}`)
          .style("left", e.pageX+10+"px")
          .style("top",  e.pageY+10+"px")
          .transition().style("opacity",1);
      })
      .on("mousemove",e=>{
        tooltip.style("left", e.pageX+10+"px")
               .style("top",  e.pageY+10+"px");
      })
      .on("mouseout",()=>tooltip.transition().style("opacity",0))
      .transition().duration(600)
        .attr('width', d=>x(d.cnt));
  }
};

document.addEventListener('DOMContentLoaded', () => CWEPage.init());
