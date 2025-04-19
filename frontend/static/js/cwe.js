(async function(){
    const data = await fetch('/api/cwe').then(r=>r.json());
    const margin = {top:20,right:20,bottom:30,left:150},
          width  = 800 - margin.left - margin.right,
          height = 400 - margin.top  - margin.bottom;
  
    const svg = d3.select("#cwe-chart").append("svg")
        .attr("width",width+margin.left+margin.right)
        .attr("height",height+margin.top+margin.bottom)
      .append("g")
        .attr("transform",`translate(${margin.left},${margin.top})`);
  
    const y = d3.scaleBand()
        .domain(data.map(d=>d.cwe))
        .range([0,height])
        .padding(0.1);
  
    const x = d3.scaleLinear()
        .domain([0, d3.max(data,d=>d.count)]).nice()
        .range([0,width]);
  
    svg.selectAll(".bar")
      .data(data)
      .enter().append("rect")
        .attr("class","bar")
        .attr("y", d=>y(d.cwe))
        .attr("height", y.bandwidth())
        .attr("x", 0)
        .attr("width", d=>x(d.count))
        .attr("fill","#FBBF24");
  
    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text").attr("class","text-gray-200");
  
    svg.append("g")
        .attr("transform",`translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5))
        .selectAll("text").attr("class","text-gray-200");
  })();
  