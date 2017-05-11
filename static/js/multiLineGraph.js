var lines = [];

function loadMultiLineGraph(error, data) {
    // set the dimensions and margins of the graph
d3.select("#multiLineGraph").select("svg").remove();
var margin = {top: 20, right: 50, bottom: 30, left: 50},
    width = 900 - margin.left - margin.right,
    height = 550 - margin.top - margin.bottom;

// parse the date / time
var parseTime = d3.timeParse("%d-%b-%y");

// set the ranges
var x = d3.scaleLinear().range([0, width]);
var y = d3.scaleLinear().range([height, 0]);

var	valueline = d3.svg.line()
    	.x(function(d, i) { return x(i); })
    	.y(function(d, i) { return y(d.pos); });


svg = d3.select("#multiLineGraph").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");


    console.log("loadMultiLineGraph");
    console.log(data);


    var color = d3.scale.category20b();

    var modData = [];
    for(i=0; i<20; i++) {
        var team = [];
        for(j=0; j<data.length; j++) {
            team.push(data[j][i]);
        }
        modData.push(team);
    }
    console.log(modData);
    // Scale the range of the data
    x.domain([0, data.length]);
    y.domain([0, data[0].length]);

    for(i=0; i<20; i++) {

        var line = svg.append("path")
            .attr("class", "line")
            .attr("id", modData[i][0].team_long_name)
            .style("stroke", color(i))
            .attr("d", valueline(modData[i]));


        svg.append("text")
            .attr("transform", "translate(" + (width+3) + "," + y(modData[i][modData[i].length-1].pos) + ")")
            .attr("dy", ".35em")
            .attr("id", modData[i][0].team_long_name)
            .attr("text-anchor", "start")
            .attr("font-size", 12)
            .style("fill", color(i))
            .on("mouseover", function(d,i) {return activateLine(d, this.id);})
            .on("mouseout", function(d,i) {return resetLines();})
            .text(modData[i][0].team_long_name);

    }



    // Add the X Axis
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));

    // Add the Y Axis
    svg.append("g")
        .call(d3.axisLeft(y));



}

function activateLine(d, id) {
    console.log("activateLine: "  + id);
    var t = d3.select("#multiLineGraph").transition()
        .duration(d3.event.altKey ? 7500 : 350);

    t.selectAll("path.line")
        .style("opacity", function(d, ii) { console.log("set opacity func" + this.id);if (this.id === id) return 1.0; else  return 0.1;});
}

function resetLines() {
    console.log("resetLines");
    var t = d3.select("#multiLineGraph").transition()
        .duration(d3.event.altKey ? 7500 : 350);

    t.selectAll("path.line")
        .style("opacity", function(d, ii) { console.log("reset opacity func");return 0.5;});

}
