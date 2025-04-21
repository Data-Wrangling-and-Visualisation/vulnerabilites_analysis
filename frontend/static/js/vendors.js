// общий тултип
const tooltip = d3.select("body")
  .append("div")
    .attr("class", "d3-tooltip");

const VendorPage = {
  vendor: '',
  data: [],

  init() {
    // установить дефолты
    this.setDefaultDates();
    // если в URL есть ?vendor=..., взять его
    const params = new URLSearchParams(window.location.search);
    this.vendor = params.get('vendor') || '';
    document.getElementById('vendor-filter').value = this.vendor;

    document.getElementById('apply-vendor')
      .addEventListener('click', () => this.onApply());

    if (this.vendor) {
      this.loadData();
    }
  },

  setDefaultDates() {
    const today = new Date(),
          lastMonth = new Date();
    lastMonth.setMonth(lastMonth.getMonth() - 1);
    document.getElementById('vendor-end').value   = today.toISOString().slice(0,10);
    document.getElementById('vendor-start').value = lastMonth.toISOString().slice(0,10);
  },

  onApply() {
    this.vendor = document.getElementById('vendor-filter').value.trim();
    if (!this.vendor) return alert('Введите имя вендора, например Microsoft');
    // обновим URL, чтобы можно было шарить ссылку
    const url = `${window.location.pathname}?vendor=${encodeURIComponent(this.vendor)}`;
    history.replaceState(null, '', url);
    this.loadData();
  },

  loadData() {
    document.getElementById('vendor-title').textContent = this.vendor;

    const start = document.getElementById('vendor-start').value;
    const end   = document.getElementById('vendor-end').value;
    const sev   = document.getElementById('vendor-severity').value;

    // соберём GET-параметры
    const p = { vendor: this.vendor };
    if (start) p.date_from = start;
    if (end)   p.date_to   = end;
    if (sev !== 'all') p.severity = sev;

    const qs = new URLSearchParams(p).toString();

    fetch(`/api/vulnerabilities?${qs}`)
      .then(r => r.json())
      .then(j => {
        // нормализуем
        this.data = j.vulnerabilities.map(v => ({
          cve_id: v.cve_id,
          date:   new Date(v.published_date.split('T')[0]),
          score:  v.cvss_v3?.base_score ?? v.cvss_v2?.base_score ?? 0,
          severity: v.cvss_v3?.severity || v.cvss_v2?.severity || 'UNKNOWN',
          attack:   v.cvss_v3?.attack_vector || v.cvss_v2?.access_vector || 'UNKNOWN'
        }));
        this.renderSeverityChart();
        this.renderTrendChart();
        this.renderTable();
      });
  },

  renderSeverityChart() {
    const counts = d3.rollup(this.data, v => v.length, d => d.severity);
    const arr = Array.from(counts, ([key, value]) => ({ key, value }));

    const color = {
      CRITICAL: '#e63946', HIGH: '#f77f00',
      MEDIUM: '#fcbf49', LOW: '#a8dadc',
      UNKNOWN: '#8d99ae'
    };

    const sel = '#vendor-severity-chart';
    const { width, height } = d3.select(sel).node().parentNode.getBoundingClientRect();
    const R = Math.min(width, height) / 2 - 20;

    const svg = d3.select(sel).html('')
      .append('svg').attr('width', width).attr('height', height)
      .append('g').attr('transform', `translate(${width/2},${height/2})`);

    const pie = d3.pie().value(d => d.value).sort(null);
    const arc = d3.arc().innerRadius(R*0.3).outerRadius(R).cornerRadius(4);

    // draw
    svg.selectAll('path')
      .data(pie(arr))
      .join('path')
        .attr('fill', d => color[d.data.key]||'#666')
        .attr('d', arc.startAngle(0).endAngle(0))
        .on('mouseover', (e,d) => {
          tooltip.html(`${d.data.key}: ${d.data.value}`)
            .style('left', e.pageX+10+'px')
            .style('top',  e.pageY+10+'px')
            .transition().style('opacity',1);
        })
        .on('mousemove', e => {
          tooltip.style('left', e.pageX+10+'px').style('top', e.pageY+10+'px');
        })
        .on('mouseout', () => tooltip.transition().style('opacity',0))
      .transition().duration(600)
        .attrTween('d', function(d) {
          const i = d3.interpolate({startAngle:0,endAngle:0}, d);
          return t => arc(i(t));
        });

    // легенда
    const legend = svg.append('g')
      .attr('transform', `translate(${-width/2+20},${-height/2+20})`);
    arr.forEach((d,i) => {
      const g = legend.append('g').attr('transform', `translate(0,${i*18})`);
      g.append('rect').attr('width',12).attr('height',12)
        .attr('fill',color[d.key]||'#666');
      g.append('text').attr('x',16).attr('y',10)
        .style('fill','#eee').style('font-size','12px')
        .text(`${d.key} (${d.value})`);
    });
  },

  renderTrendChart() {
    const arr = Array.from(
      d3.rollup(this.data, vs => vs.length, d => d.date.toISOString().split('T')[0]),
      ([dt, cnt]) => ({ date:new Date(dt), cnt })
    ).sort((a,b)=>a.date - b.date);

    const sel = '#vendor-trend-chart';
    const { width, height } = d3.select(sel).node().parentNode.getBoundingClientRect();
    const m = { top:20, right:20, bottom:60, left:50 };
    const W = width - m.left - m.right;
    const H = height - m.top - m.bottom;

    const svg = d3.select(sel).html('')
      .append('svg').attr('width',width).attr('height',height)
      .append('g').attr('transform',`translate(${m.left},${m.top})`);

    const x = d3.scaleTime().domain(d3.extent(arr,d=>d.date)).range([0,W]);
    const y = d3.scaleLinear().domain([0,d3.max(arr,d=>d.cnt)]).nice().range([H,0]);

    // axes
    svg.append('g').attr('transform',`translate(0,${H})`)
      .call(d3.axisBottom(x).ticks(6).tickFormat(d3.timeFormat('%d %b')))
      .selectAll('text').attr('transform','rotate(-45)').style('text-anchor','end');
    svg.append('g').call(d3.axisLeft(y).ticks(5));

    // line
    const line = d3.line().curve(d3.curveMonotoneX)
      .x(d=>x(d.date)).y(d=>y(d.cnt));

    svg.append('path')
      .datum(arr)
      .attr('fill','none').attr('stroke','var(--accent-from)').attr('stroke-width',2)
      .attr('d',line)
      .transition().duration(600)
        .attrTween('stroke-dasharray', function(){
          const len = this.getTotalLength();
          return t=>`${t*len},${len}`;
        });

    // dots
    svg.selectAll('circle')
      .data(arr).join('circle')
        .attr('cx',d=>x(d.date)).attr('cy',d=>y(d.cnt)).attr('r',4)
        .attr('fill','var(--accent-to)')
        .on('mouseover',(e,d)=>{
          tooltip.html(`${d3.timeFormat('%Y-%m-%d')(d.date)}<br>Count: ${d.cnt}`)
            .style('left',e.pageX+10+'px').style('top',e.pageY+10+'px')
            .transition().style('opacity',1);
        })
        .on('mousemove', e=>tooltip.style('left',e.pageX+10+'px').style('top',e.pageY+10+'px'))
        .on('mouseout', ()=>tooltip.transition().style('opacity',0));
  },

  renderTable() {
    const tbody = document.querySelector('#vendor-table tbody');
    tbody.innerHTML = '';
    this.data.forEach(v => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${v.cve_id}</td>
        <td>${v.date.toISOString().split('T')[0]}</td>
        <td>${v.score.toFixed(1)}</td>
        <td>${v.severity}</td>
        <td>${v.attack}</td>
      `;
      tbody.appendChild(tr);
    });
  }
};

document.addEventListener('DOMContentLoaded', () => VendorPage.init());
