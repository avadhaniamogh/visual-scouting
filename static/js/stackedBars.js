var params = [] ;
var stat = "overall";
var mode = "stacked";
var existingData;
var dragStartX = 0;
var dragEndX = 0;

//sorting:0 = no sort, 1= asc, 2= desc
function loadStackedBars(error, data, fromMenu, sorting) {
    console.log("loadStackedBars");
    console.log(data);
    existingData = data;
    d3.select("#stackedBars").select("g").remove();
    var sortingData = existingData[stat];
    var minGD = Number.MAX_SAFE_INTEGER;
    for(i=0; i<sortingData.length; i++) {
        if(sortingData[i]["GD"] < minGD)
            minGD = sortingData[i]["GD"];
    }
    minGD = minGD - 1;

    function compareFunc(a, b) {
        var aTotal = 0;
        var bTotal = 0;
        for(i=0; i<params.length; i++) {
            var key = params[i];

            if(key === "Pos") {
                aTotal = aTotal + (21-a[key]);
                bTotal = bTotal + (21-b[key]);
            } else if(key === "GD") {
                aTotal = aTotal + a[key] + Math.abs(minGD);
                bTotal = bTotal + b[key] + Math.abs(minGD);
            } else {
                aTotal = aTotal + a[key];
                bTotal = bTotal + b[key];
                console.log("Value added:" + a[key]);
                console.log("Value added:" + b[key]);
            }
        }
        if(sorting === 1) {
            if (aTotal < bTotal) {
                return -1;
            }
            if (aTotal > bTotal) {
                return 1;
            }
        } else if(sorting === 2) {
            if (aTotal > bTotal) {
                return -1;
            }
            if (aTotal < bTotal) {
                return 1;
            }
        }


        return 0;
    }



    if(sorting != 0) {
        sortingData = existingData[stat].slice();
        sortingData = sortingData.sort(compareFunc);
        console.log("Sorted data: ");
        console.log(sortingData);
    }

    var n = params.length, // The number of series.
        m = data[stat].length; // The number of values per series.

    // The xz array has m elements, representing the x-values shared by all series.
    // The yz array has n elements, representing the y-values of each of the n series.
    // Each yz[i] is an array of m non-negative numbers representing a y-value for xz[i].
    // The y01z array has the same structure as yz, but with stacked [y₀, y₁] instead of y.
    var xz = d3.range(m),
        yz = d3.range(n).map(function(i) { return getSelectedData(m, params[i]); }),
        y01z = d3.stack().keys(d3.range(n))(d3.transpose(yz)),
        yMax = d3.max(yz, function(y) { return d3.max(y); }),
        y1Max = d3.max(y01z, function(y) { return d3.max(y, function(d) { return d[1]; }); });

    var svg = d3.select("#stackedBars"),
        margin = {top: 40, right: 10, bottom: 20, left: 10},
        width = +svg.attr("width") - margin.left - margin.right,
        height = +svg.attr("height") - margin.top - margin.bottom,
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.scaleBand()
        .domain(xz)
        .rangeRound([0, width])
        .padding(0.08);

    var y = d3.scaleLinear()
        .domain([0, y1Max + 100])
        .range([height, 0]);

    var color = d3.scaleOrdinal()
        .domain(d3.range(n))
        .range(d3.schemeSet2);

    var series = g.selectAll(".series")
      .data(y01z)
      .enter().append("g")
        .attr("fill", function(d, i) { return color(i); });

    var rect = series.selectAll("rect")
      .data(function(d) { return d; })
      .enter().append("rect")
        .attr("x", function(d, i) { return x(i); })
        .attr("y", height)
        .attr("width", x.bandwidth())
        .attr("height", 0);

    rect.transition()
        .delay(function(d, i) { return i * 10; })
        .attr("y", function(d) { return y(d[1]); })
        .attr("height", function(d) { return y(d[0]) - y(d[1]); });

    g.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x)
            .tickSize(0)
            .tickFormat(function(d,i){ return sortingData[i].short_name;})
            .tickPadding(6));


    d3.selectAll("input")
        .on("change", changed);
    svg.call(d3.drag().on("start", dragStart).on("end", dragEnd));

    if (fromMenu) {
        var timeout = d3.timeout(function() {
          d3.select("input[value=\"grouped\"]")
              .property("checked", true)
              .dispatch("change");
        }, 2000);
    } else {
        var timeout = d3.timeout(function() {
          d3.select("input[value=\"grouped\"]")
              .property("checked", true)
              .dispatch("change");
        }, 200);
    }


    function changed() {
      if(fromMenu)
        timeout.stop();
      if (this.value === "grouped") transitionGrouped();
      else transitionStacked();
    }

    function transitionGrouped() {
      y.domain([0, yMax]);

      rect.transition()
          .duration(500)
          .delay(function(d, i) { return i * 10; })
          .attr("x", function(d, i) { return x(i) + x.bandwidth() / n * this.parentNode.__data__.key; })
          .attr("width", x.bandwidth() / n)
        .transition()
          .attr("y", function(d) { return y(d[1] - d[0]); })
          .attr("height", function(d) { return y(0) - y(d[1] - d[0]); });
    }

    function transitionStacked() {
      y.domain([0, y1Max]);

      rect.transition()
          .duration(500)
          .delay(function(d, i) { return i * 10; })
          .attr("y", function(d) { return y(d[1]); })
          .attr("height", function(d) { return y(d[0]) - y(d[1]); })
          .transition()
          .attr("x", function(d, i) { return x(i); })
          .attr("width", x.bandwidth());
    }


    function getSelectedData(m, param) {

      var values = [];
      console.log("Param name: " + param);


      for (i = 0; i < m; ++i) {
        if(param === "Pos")
            values[i] = 21 - sortingData[i][param]; //position 1 should have the biggest bar
        else if(param === "GD")
            values[i] = sortingData[i][param] + Math.abs(minGD);
        else
            values[i] = sortingData[i][param];
      }
      console.log("Values: " + values);
      return values;
    }


    var dataset = [
        [

        ],
        [

        ],
        [

        ]
    ];

    var color_hash = {  0 : ["apple", "green"],
					    1 : ["mango", "orange"],
					    2 : ["cherry", "red"]
					  }

    // add legend
    console.log("add legend");
	var legend = svg.append("g")
	  .attr("class", "legend")
	  .attr("x", margin.left)
	  .attr("y", margin.top)
	  .attr("height", 100)
	  .attr("width", 100);

	legend.selectAll('g').data(dataset)
      .enter()
      .append('g')
      .each(function(d, i) {
        var g = d3.select(this);
        g.append("rect")
          .attr("x", margin.left + i*100)
          .attr("y", margin.top)
          .attr("width", 10)
          .attr("height", 10)
          .style("fill", color_hash[String(i)][1]);

        g.append("text")
          .attr("x", margin.left + i*100 + 15)
          .attr("y", margin.top + 8)
          .attr("height",30)
          .attr("width",100)
          .style("fill", color_hash[String(i)][1])
          .text(color_hash[String(i)][0]);

      });


}

function onParamChanged(checkbox) {
    var key = checkbox.id;
    if(checkbox.checked) {
        params.push(key);
    } else {
        var index = params.indexOf(key);
        if (index > -1) {
            params.splice(index, 1);
        }
    }

    loadStackedBars(undefined, existingData, false, 0);

}

function dragStart() {
		console.log("Drag started");
		var coordinates = [0, 0];
		coordinates = d3.mouse(this);
		var x = coordinates[0];
		var y = coordinates[1];
		dragStartX = x;
	}

function dragEnd() {
		console.log("Drag ended");
		var coordinates = [0, 0];
		coordinates = d3.mouse(this);
		var x = coordinates[0];
		var y = coordinates[1];
		dragEndX= x;
		var diff = dragEndX - dragStartX;
		if(diff < 0) {
            console.log("Descending");
            loadStackedBars(undefined, existingData, true, 2);
		} else if(diff > 0) {
            console.log("Ascending");
            loadStackedBars(undefined, existingData, true, 1);
		}
		console.log("Diff: " + diff);
	}

function onModeChanged(radio) {
    mode = radio.id;
    // loadStackedBars(undefined, existingData, true, 0);
}

function onStatChanged(radio) {
    stat = radio.id;
    loadStackedBars(undefined, existingData, false, 0);
}

function menuChanged(error, data) {
    params.length = 0;
    params.push("Pos");
    params.push("Pts");
    params.push("W");
    params.push("L");
    params.push("D");
    params.push("GF");
    params.push("GA");
    params.push("GD");
    params.push("CS");
    mode = "stacked";
    stat = "overall";
    for(i=0; i<params.length; i++) {
        var key = params[i];
        console.log(key);
        document.getElementById(key).checked = true;
    }
    document.getElementById(mode).checked = true;
    document.getElementById(stat).checked = true;
    loadStackedBars(error, data, true, 0);

}
