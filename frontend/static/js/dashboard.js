document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        // 1) вытягиваем массив объектов {severity, count}
        let stats = data.severity_stats || [];
  
        // 2) убираем пустые severity
        stats = stats.filter(d => d.severity);
  
        // 3) задаём нужный нам порядок
        const order = ['LOW','MEDIUM','HIGH','CRITICAL'];
  
        // 4) приводим к [ [label, value], … ], заполняя нулями, если какой‑то нет
        const entries = order.map(sev => {
          const found = stats.find(d => d.severity === sev);
          return [sev, found ? found.count : 0];
        });
  
        const margin = { top: 20, right: 20, bottom: 50, left: 40 };
        const width  = 600 - margin.left - margin.right;
        const height = 400 - margin.top  - margin.bottom;
  
        // 5) создаём SVG
        const svg = d3.select('#chart')
          .append('svg')
            .attr('width',  width  + margin.left + margin.right)
            .attr('height', height + margin.top  + margin.bottom)
          .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
  
        // 6) шкалы
        const x = d3.scaleBand()
          .domain(entries.map(d => d[0]))
          .range([0, width])
          .padding(0.1);
  
        const y = d3.scaleLinear()
          .domain([0, d3.max(entries, d => d[1])])
          .nice()
          .range([height, 0]);
  
        // 7) рисуем бары
        svg.selectAll('.bar')
          .data(entries)
          .enter().append('rect')
            .attr('class', 'bar')
            .attr('x',      d => x(d[0]))
            .attr('width',  x.bandwidth())
            .attr('y',      d => y(d[1]))
            .attr('height', d => height - y(d[1]));
  
        // 8) оси
        svg.append('g')
           .attr('transform', `translate(0,${height})`)
           .call(d3.axisBottom(x))
           .selectAll("text")
             .attr("transform", "translate(0,5)") // чуть опускаем
             .style("text-anchor", "middle");
  
        svg.append('g')
           .call(d3.axisLeft(y));
      })
      .catch(err => console.error(err));
  });
  