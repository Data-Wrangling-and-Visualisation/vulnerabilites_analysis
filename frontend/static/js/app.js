const App = {
    data: [],
  
    init() {
      this.bindEvents();
      this.setDefaultDates();
      this.fetchData();
    },
  
    bindEvents() {
      document.getElementById('apply-filters')
              .addEventListener('click', () => this.applyFilters());
      document.getElementById('update-data')
              .addEventListener('click', () => this.updateData());
    },
  
    setDefaultDates() {
      const today = new Date(),
            lastMonth = new Date();
      lastMonth.setMonth(lastMonth.getMonth() - 1);
  
      document.getElementById('date-to').value   = today.toISOString().slice(0,10);
      document.getElementById('date-from').value = lastMonth.toISOString().slice(0,10);
    },
  
    flatten(raw) {
      return raw.map(v => ({
        cve_id:        v.cve_id,
        published_date:v.published_date.split('T')[0],
        cvss_score:    v.cvss_v3?.base_score ?? v.cvss_v2?.base_score ?? 0,
        severity:      v.cvss_v3?.severity     || v.cvss_v2?.severity     || 'UNKNOWN',
        attack_vector: v.cvss_v3?.attack_vector|| v.cvss_v2?.access_vector || 'UNKNOWN',
        cwe:           v.cwe
      }));
    },
  
    fetchData(params = {}) {
      const qs = new URLSearchParams(params).toString();
      fetch(`/api/vulnerabilities?${qs}`)
        .then(res => res.json())
        .then(json => {
          this.data = this.flatten(json.vulnerabilities || []);
          this.renderCharts();
          this.renderTable();
        });
    },
  
    applyFilters() {
      const sev  = document.getElementById('severity-filter').value;
      const from = document.getElementById('date-from').value;
      const to   = document.getElementById('date-to').value;
      const p = {};
      if (sev !== 'all') p.severity = sev;
      if (from) p.date_from = from;
      if (to)   p.date_to   = to;
      this.fetchData(p);
    },
  
    updateData() {
      const btn = document.getElementById('update-data');
      btn.disabled = true; btn.textContent = 'Обновляю…';
      fetch('/api/update', { method: 'POST' })
        .then(r => r.json())
        .then(()=> this.fetchData())
        .finally(()=>{
          btn.disabled = false;
          btn.textContent = 'Обновить';
        });
    },
  
    renderCharts() {
      this.renderSeverityChart();
      this.renderCVSSTimeSeries();
      this.renderAttackVectorChart();
      this.renderTopCWEChart();
    },
  
    renderSeverityChart() {
      const data = this.data;
      const counts = d3.rollup(data, v=>v.length, d=>d.severity);
      const arr = Array.from(counts, ([k,v])=>({k,v}));
  
      const container = d3.select('#severity-distribution').node().parentNode;
      const { width, height } = container.getBoundingClientRect();
      const margin = 20;
      const R = Math.min(width, height)/2 - margin;
  
      const color = d3.scaleOrdinal(d3.schemeSet2);
      const pie   = d3.pie().value(d=>d.v);
      const arc   = d3.arc().innerRadius(R*0.3).outerRadius(R);
  
      const svg = d3.select('#severity-distribution').html('')
        .append('svg')
          .attr('width',  width)
          .attr('height', height)
        .append('g')
          .attr('transform', `translate(${width/2},${height/2})`);
  
      svg.selectAll('path')
        .data(pie(arr))
        .join('path')
          .attr('d', arc)
          .attr('fill', d=>color(d.data.k))
        .append('title')
          .text(d=>`${d.data.k}: ${d.data.v}`);
  
      svg.selectAll('text.slice-label')
        .data(pie(arr))
        .join('text')
          .attr('class','slice-label')
          .attr('transform', d=>`translate(${arc.centroid(d)})`)
          .attr('dy','0.35em')
          .attr('text-anchor','middle')
          .style('fill','var(--text-light)')
          .style('font-size','12px')
          .text(d=>d.data.k);
    },
  
    renderCVSSTimeSeries() {
      const data = this.data;
      const parse = d3.timeParse('%Y-%m-%d');
      let series = data.map(d=>({
        date:  parse(d.published_date),
        score: d.cvss_score
      })).filter(d=>d.date && !isNaN(d.score));
      series.sort((a,b)=>a.date-b.date);
  
      const container = d3.select('#cvss-scores-over-time').node().parentNode;
      const { width, height } = container.getBoundingClientRect();
      const margin = {top:20, right:20, bottom:60, left:50};
      const W = width - margin.left - margin.right;
      const H = height - margin.top - margin.bottom;
  
      const svg = d3.select('#cvss-scores-over-time').html('')
        .append('svg')
          .attr('width',  width)
          .attr('height', height)
        .append('g')
          .attr('transform', `translate(${margin.left},${margin.top})`);
  
      const x = d3.scaleTime()
        .domain(d3.extent(series, d=>d.date)).range([0,W]);
      const y = d3.scaleLinear().domain([0,10]).range([H,0]);
  
      svg.append('g')
        .attr('transform',`translate(0,${H})`)
        .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat('%d %b')))
        .selectAll('text').attr('transform','rotate(-45)').style('text-anchor','end');
      svg.append('g').call(d3.axisLeft(y));
  
      const line = d3.line().x(d=>x(d.date)).y(d=>y(d.score));
      svg.append('path')
        .datum(series)
        .attr('fill','none')
        .attr('stroke','var(--accent-from)')
        .attr('stroke-width',2)
        .attr('d',line);
  
      svg.append('g').selectAll('circle')
        .data(series).join('circle')
          .attr('cx',d=>x(d.date))
          .attr('cy',d=>y(d.score))
          .attr('r',3)
          .attr('fill','var(--accent-to)')
        .append('title')
          .text(d=>`${d3.timeFormat('%Y-%m-%d')(d.date)} — ${d.score}`);
    },
  
    renderAttackVectorChart() {
      const data = this.data;
      const counts = d3.rollup(data, v=>v.length, d=>d.attack_vector);
      const arr = Array.from(counts, ([k,v])=>({k,v})).sort((a,b)=>b.v-a.v);
  
      const container = d3.select('#attack-vector-distribution').node().parentNode;
      const { width, height } = container.getBoundingClientRect();
      const margin = {top:20, right:20, bottom:20, left:100};
      const W = width - margin.left - margin.right;
      const H = height - margin.top - margin.bottom;
  
      const svg = d3.select('#attack-vector-distribution').html('')
        .append('svg')
          .attr('width',  width)
          .attr('height', height)
        .append('g')
          .attr('transform',`translate(${margin.left},${margin.top})`);
  
      const x = d3.scaleLinear().domain([0, d3.max(arr,d=>d.v)]).range([0,W]);
      const y = d3.scaleBand(arr.map(d=>d.k), [0,H]).padding(0.2);
  
      svg.selectAll('rect')
        .data(arr).join('rect')
          .attr('y',d=>y(d.k))
          .attr('width',d=>x(d.v))
          .attr('height',y.bandwidth())
          .attr('fill','var(--accent-from)');
  
      svg.append('g').call(d3.axisLeft(y)).selectAll('text')
        .style('fill','var(--text-light)');
    },
  
    renderTopCWEChart() {
      const data = this.data;
      const counts = d3.rollup(data, v=>v.length, d=>d.cwe);
      const arr = Array.from(counts, ([k,v])=>({k,v}))
        .sort((a,b)=>b.v-a.v).slice(0,10);
  
      const container = d3.select('#top-cwe').node().parentNode;
      const { width, height } = container.getBoundingClientRect();
      const margin = {top:20, right:20, bottom:60, left:60};
      const W = width - margin.left - margin.right;
      const H = height - margin.top - margin.bottom;
  
      const svg = d3.select('#top-cwe').html('')
        .append('svg')
          .attr('width',  width)
          .attr('height', height)
        .append('g')
          .attr('transform',`translate(${margin.left},${margin.top})`);
  
      const x = d3.scaleBand(arr.map(d=>d.k), [0,W]).padding(0.2);
      const y = d3.scaleLinear().domain([0, d3.max(arr,d=>d.v)]).range([H,0]);
  
      svg.append('g').call(d3.axisLeft(y));
      svg.append('g').attr('transform',`translate(0,${H})`)
        .call(d3.axisBottom(x))
        .selectAll('text').attr('transform','rotate(-45)').style('text-anchor','end').style('fill','var(--text-light)');
  
      svg.selectAll('rect')
        .data(arr).join('rect')
          .attr('x',d=>x(d.k))
          .attr('y',d=>y(d.v))
          .attr('width',x.bandwidth())
          .attr('height',d=>H-y(d.v))
          .attr('fill','var(--accent-to)');
    },
  
    renderTable() {
      const tbody = document.querySelector('#vulnerabilities-table tbody');
      tbody.innerHTML = '';
      this.data.slice(0,20).forEach(v=>{
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${v.cve_id}</td>
          <td>${v.published_date}</td>
          <td>${v.cvss_score.toFixed(1)}</td>
          <td>${v.severity}</td>
          <td>${v.attack_vector}</td>
        `;
        tbody.appendChild(row);
      });
    }
  };
  
  document.addEventListener('DOMContentLoaded', () => App.init());
  