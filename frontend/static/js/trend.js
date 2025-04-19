(async function() {
    // --- 1) Load data ---
    let raw = await fetch('/api/trend').then(r => r.json());
    raw = raw.map(d => ({ date: new Date(d.date), count: d.count }));
  
    // --- 2) Init flatpickr ---
    const minDate = d3.min(raw, d => d.date);
    const maxDate = d3.max(raw, d => d.date);
    flatpickr("#date-start", { defaultDate: minDate,  minDate, maxDate });
    flatpickr("#date-end",   { defaultDate: maxDate, minDate, maxDate });
  
    // --- 3) Create full‑screen SVG ---
    const margin = { top:60, right:40, bottom:40, left:60 };
    const width  = window.innerWidth  - margin.left - margin.right;
    const height = window.innerHeight - margin.top  - margin.bottom;
  
    const svg = d3.select("#chart").append("svg")
        .attr("width",  width + margin.left + margin.right)
        .attr("height", height + margin.top  + margin.bottom)
      .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
  
    // --- 4) Scales & Axes groups ---
    const x = d3.scaleUtc().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);
    const xAxisG = svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .attr("class","axis text-gray-200");
    const yAxisG = svg.append("g")
        .attr("class","axis text-gray-200");
  
    // --- 5) Line generator ---
    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.count))
        .curve(d3.curveMonotoneX);
  
    // --- 6) Clip for zoom ---
    svg.append("defs").append("clipPath")
      .attr("id","clip")
      .append("rect")
        .attr("width", width)
        .attr("height", height);
  
    // --- 7) Path container ---
    const pathG = svg.append("g").attr("clip-path","url(#clip)");
    pathG.append("path")
      .datum(raw)
      .attr("class","line")
      .attr("stroke","#4F46E5")
      .attr("stroke-width",2)
      .attr("fill","none");
  
    // --- 8) Tooltip focus ---
    const focus = svg.append("g").style("display","none");
    focus.append("circle").attr("r",4).attr("fill","#4F46E5");
    const tooltip = d3.select("#tooltip");
  
    // --- 9) Zoom behavior ---
    const zoom = d3.zoom()
      .scaleExtent([1,10])
      .translateExtent([[0,0],[width,height]])
      .extent([[0,0],[width,height]])
      .on("zoom", zoomed);
  
    svg.append("rect")
      .attr("class","zoom")
      .attr("width", width).attr("height", height)
      .style("fill","none").style("pointer-events","all")
      .call(zoom);
  
    // --- Render function ---
    function render(data) {
      x.domain(d3.extent(data, d => d.date));
      y.domain([0, d3.max(data, d => d.count)]).nice();
      svg.select(".line").datum(data).attr("d", line);
      xAxisG.call(d3.axisBottom(x).ticks(width/80).tickSizeOuter(0));
      yAxisG.call(d3.axisLeft(y));
    }
  
    render(raw); // initial draw
  
    // --- Filtering ---
    function applyFilters() {
      let d = raw;
      // Date range
      const ds = document.getElementById("date-start")._flatpickr.selectedDates[0];
      const de = document.getElementById("date-end")._flatpickr.selectedDates[0];
      d = d.filter(p => p.date >= ds && p.date <= de);
      // TODO: severity & text-search
      render(d);
    }
    ["date-start","date-end","severity-filter","search-input"]
      .forEach(id => document.getElementById(id)
        .addEventListener("change", applyFilters));
  
    // --- Tooltip interactions ---
    const bisect = d3.bisector(d => d.date).left;
    svg.append("rect")
      .attr("width", width).attr("height", height)
      .style("fill","none").style("pointer-events","all")
      .on("mouseover", () => focus.style("display", null))
      .on("mouseout",  () => { focus.style("display","none"); tooltip.style("opacity",0); })
      .on("mousemove", function(event) {
        const xm = d3.pointer(event,this)[0];
        const xd = x.invert(xm);
        const i  = bisect(raw, xd, 1);
        const d0 = raw[i-1], d1 = raw[i] || d0;
        const d  = xd - d0.date > d1.date - xd ? d1 : d0;
        focus.attr("transform", `translate(${x(d.date)},${y(d.count)})`);
        tooltip
          .style("opacity",1)
          .style("left", (event.pageX+10) + "px")
          .style("top",  (event.pageY-30) + "px")
          .html(`<strong>${d3.timeFormat("%Y-%m-%d")(d.date)}</strong><br/>${d.count}`);
      });
  
    // --- Zoom handler ---
    function zoomed(event) {
      const zx = event.transform.rescaleX(x);
      xAxisG.call(d3.axisBottom(zx));
      svg.select(".line").attr("d", line.x(d => zx(d.date)));
    }
  
    // Reload on resize
    window.addEventListener("resize", () => location.reload());
  })();
  