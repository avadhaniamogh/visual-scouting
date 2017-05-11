var w = window.innerWidth*0.68*0.95;
var h = Math.ceil(w*0.7);
var oR = 0;
var nTop = 0;
var currentSelectedId = "";

var svgContainer = d3.select("#mainBubble")
   .style("height", h+"px");

var svg = d3.select("#mainBubble").append("svg")
     .attr("class", "mainBubbleSVG")
     .attr("width", w)
     .attr("height",h)
     .on("mouseleave", function() {return resetBubbles();});

var mainNote = svg.append("text")
 .attr("id", "bubbleItemNote")
 .attr("x", 10)
 .attr("y", w/2-15)
 .attr("font-size", 15)
 .attr("dominant-baseline", "middle")
 .attr("alignment-baseline", "middle")
 .style("fill", "#888888")
 .text(function(d) {return "Select a country to view details";});

var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);


function initMenu(error, root) {
     console.log(error);

     var bubbleObj = svg.selectAll(".topBubble")
             .data(root)
         .enter().append("g")
             .attr("id", function(d,i) {return "topBubbleAndText_" + i});

     console.log(root);
     nTop = root.length;
     oR = w/(1+3*nTop);

 h = Math.ceil(w/nTop*2);
 svgContainer.style("height",h+"px");

     var colVals = d3.scale.category10();

     bubbleObj.append("circle")
         .attr("class", "topBubble")
         .attr("id", function(d,i) {return "topBubble" + i;})
         .attr("r", function(d) { return oR; })
         .attr("cx", function(d, i) {return oR*(3*(1+i)-1);})
         .attr("cy", (h+oR)/3)
         .style("fill", function(d,i) { return colVals(i); })
         .style("opacity",0.3)
         .on("mouseover", function(d,i) {return activateBubble(d,i);})
         .on("click", function (d, i) {
             if(currentSelectedId != "") {
                 d3.select(currentSelectedId).style("stroke-width", 0);
                 d3.select(currentSelectedId).style("stroke", colVals[i]);
             }
             currentSelectedId = "#topBubble" + i;
             d3.select(this).style("stroke-width", 5);
             d3.select(this).style("stroke", colVals[i]);
             d3.select("#bubbleItemNote").text("Viewing details of " + d.country_name);

             document.getElementById("contentArea").style.visibility = "visible";
             document.getElementById("contentArea").style.display= 'block';
             var url = "/data/stats?country_id=" + d.country_id;
             console.log(url);
             queue().defer(d3.json, url).await(menuChanged);

             var url2 = "/data/standings?country_id=" + d.country_id;
             queue().defer(d3.json, url2).await(loadMultiLineGraph);
         });


     bubbleObj.append("text")
         .attr("class", "topBubbleText")
         .attr("x", function(d, i) {return oR*(3*(1+i)-1);})
         .attr("y", (h+oR)/3)
         .style("fill", function(d,i) { return colVals(i); })
         .attr("font-size", 30)
         .attr("text-anchor", "middle")
         .attr("dominant-baseline", "middle")
         .attr("alignment-baseline", "middle")
         .text(function(d) {return d.country_name})
         .on("mouseover", function(d,i) {return activateBubble(d,i);})
         .on("click", function (d, i) {
             if(currentSelectedId != "") {
                 d3.select(currentSelectedId).style("stroke-width", 0);
                 d3.select(currentSelectedId).style("stroke", colVals[i]);
             }
             currentSelectedId = this.id;
             d3.select("#topBubble" + i).style("stroke-width", 5);
             d3.select("#topBubble" + i).style("stroke", colVals[i]);
             d3.select("#bubbleItemNote").text("Viewing details of " + d.country_name);

             document.getElementById("contentArea").style.visibility = "visible";
             document.getElementById("contentArea").style.display= 'block';


             var url = "/data/stats?country_id=" + d.country_id;
             console.log(url);
             queue().defer(d3.json, url).await(menuChanged);

             var url2 = "/data/standings?country_id=" + d.country_id;
             queue().defer(d3.json, url2).await(loadMultiLineGraph);
         });


     for(var iB = 0; iB < nTop; iB++)
     {
         var childBubbles = svg.selectAll(".childBubble" + iB)
             .data(root[iB].teams)
             .enter().append("g");

     //var nSubBubble = Math.floor(root.children[iB].children.length/2.0);

         childBubbles.append("circle")
             .attr("class", "childBubble" + iB)
             .attr("id", function(d,i) {return "childBubble_" + iB + "sub_" + i;})
             .attr("r",  function(d) {return oR/3.0;})
             .attr("cx", function(d,i) {return (oR*(3*(iB+1)-1) + oR*1.5*Math.cos((i-1)*18/180*3.1415926));})
             .attr("cy", function(d,i) {return ((h+oR)/3 +        oR*1.5*Math.sin((i-1)*18/180*3.1415926));})
             .attr("cursor","pointer")
             .style("opacity",0.4)
             .style("fill", "#eee")
            .on("mouseout", function(d) {
                d3.select(this).style("opacity", 0.4);
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .on("mouseover", function(d,i) {
                d3.select(this).style("opacity", 0.8);
               div.transition()
                   .duration(200)
                   .style("opacity", 0.8);
               div	.html(d.long_name)
                   .style("left", (d3.event.pageX) + "px")
                   .style("top", (d3.event.pageY - 28) + "px");
               })
             .append("svg:title");

         childBubbles.append("text")
             .attr("class", "childBubbleText" + iB)
             .attr("x", function(d,i) {return (oR*(3*(iB+1)-1) + oR*1.5*Math.cos((i-1)*18/180*3.1415926));})
             .attr("y", function(d,i) {return ((h+oR)/3 +        oR*1.5*Math.sin((i-1)*18/180*3.1415926));})
             .style("opacity",0.4)
             .attr("text-anchor", "middle")
         .style("fill", function(d,i) { return colVals(iB); }) // #1f77b4
             .attr("font-size", 6)
             .attr("cursor","pointer")
             .attr("dominant-baseline", "middle")
             .on("mouseout", function(d,i) {
                 d3.select("#childBubble_" + iB + "sub_" + i).style("opacity", 0.4);
                 div.transition()
                     .duration(500)
                     .style("opacity", 0);
             })
             .on("mouseover", function(d,i) {
                 d3.select("#childBubble_" + iB + "sub_" + i).style("opacity", 0.8);
                div.transition()
                    .duration(200)
                    .style("opacity", .8);
                div	.html(d.long_name)
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY - 28) + "px");
                })
         .attr("alignment-baseline", "middle")
             .text(function(d) {return d.short_name});

     }

     resetBubbles();

}

 resetBubbles = function () {
   w = window.innerWidth;

   oR = w/(1+10*nTop);
   h = 250

   svgContainer.style("height",h+"px");

   mainNote.attr("y",h-15);

   svg.attr("width", w);
   svg.attr("height",h);

   // d3.select("#bubbleItemNote").text("Display Selected Item Text Here");

   var t = svg.transition()
       .duration(650);

     t.selectAll(".topBubble")
         .attr("r", function(d) { return oR; })
         .attr("cx", function(d, i) {return oR*(8.5*(1+i)-1);})
         .attr("cy", (h+oR)/3)
         .style("opacity", 0.3);

     t.selectAll(".topBubbleText")
     .attr("font-size", 30)
         .attr("x", function(d, i) {return oR*(8.5*(1+i)-1);})
         .attr("y", (h+oR)/3);

   for(var k = 0; k < nTop; k++)
   {
     t.selectAll(".childBubbleText" + k)
             .attr("x", function(d,i) {return (oR*(8.5*(k+1)-1) + oR*1.5*Math.cos((i-1)*18/180*3.1415926));})
             .attr("y", function(d,i) {return ((h+oR)/3 +        oR*1.5*Math.sin((i-1)*18/180*3.1415926));})
         .attr("font-size", 3)
             .style("opacity",0.5);

     t.selectAll(".childBubble" + k)
             .attr("r",  function(d) {return oR/5.0;})
         .style("opacity",0.5)
             .attr("cx", function(d,i) {return (oR*(8.5*(k+1)-1) + oR*1.5*Math.cos((i-1)*18/180*3.1415926));})
             .attr("cy", function(d,i) {return ((h+oR)/3 +        oR*1.5*Math.sin((i-1)*18/180*3.1415926));});

   }
 }


     function activateBubble(d,i) {
         // increase this bubble and decrease others
         var t = svg.transition()
             .duration(d3.event.altKey ? 7500 : 350);

         t.selectAll(".topBubble")
             .attr("cx", function(d,ii){
                 if(i == ii) {
                     // Nothing to change
                     return oR*(8.5*(1+ii)-1);
                 } else {
                     // Push away a little bit
                     if(ii < i){
                         // left side
                         return oR*(8.5*(1+ii)-1) - 75 * (ii+1);
                     } else {
                         // right side
                         return oR*(8.5*(1+ii)-1) + 75 * (nTop  - ii);
                     }
                 }
             })
             .style("opacity", function(d, ii) { if (i == ii) return 0.7; else  return 0.3;})
             .attr("r", function(d, ii) {
                 if(i == ii)
                     return oR*1.2;
                 else
                     return oR*0.8;
                 });

         t.selectAll(".topBubbleText")
             .attr("x", function(d,ii){
                 if(i == ii) {
                     // Nothing to change
                     return oR*(8.5*(1+ii)-1);
                 } else {
                     // Push away a little bit
                     if(ii < i){
                         // left side
                         return oR*(8.5*(1+ii)-1) - 75 * (ii+1);
                     } else {
                         // right side
                         return oR*(8.5*(1+ii)-1) + 75 * (nTop  - ii);
                     }
                 }
             })
             .attr("font-size", function(d,ii){
                 if(i == ii)
                     return 30*0.7;
                 else
                     return 30*0.8;
             });

         var signSide = -1;
         console.log("nTop: " + nTop);
         for(var k = 0; k < nTop; k++)
         {
             signSide = 1;
             if(k < nTop/2) signSide = 1;
             t.selectAll(".childBubbleText" + k)

                 .attr("x", function(d,i) { if(i<10)return (oR*(8.5*(1+k)-1) + signSide*oR*2.5*Math.cos((i-1)*36/180*3.1415926));
                 else if(i>=10 && i<15)return (oR*(8.5*(1+k)-1) + 150);   else return (oR*(8.5*(1+k)-1) - 150);})
                 .attr("y", function(d,i) {if (i < 10) return ((h + oR) / 3 + signSide * oR * 2.2 * Math.sin((i - 1) * 36 / 180 * 3.1415926));
                 else if (i>=10 && i<15) return (((h)/5) * ((i%10)) + 25); else return (((h)/5) * ((i%10)-5) + 25);})
                 .attr("font-size", function(){
                         return (k==i)?8:4;
                     })
                 .style("opacity",function(){
                         return (k==i)?1:0;
                     });

             t.selectAll(".childBubble" + k)
                 .attr("cx", function(d,i) {if(i<10)return (oR*(8.5*(1+k)-1) + signSide*oR*2.5*Math.cos((i-1)*36/180*3.1415926));
                 else if(i>=10 && i<15)return (oR*(8.5*(1+k)-1) + 150);   else return (oR*(8.5*(1+k)-1) - 150);})
                 .attr("cy", function(d,i) {if(i<10) return ((h+oR)/3 + signSide*oR*2.2*Math.sin((i-1)*36/180*3.1415926));
                 else if (i>=10 && i<15) return (((h)/5) * ((i%10)) + 25); else return (((h)/5) * ((i%10)-5) + 25);})
                 .attr("r", function(){
                         return (k==i)?(oR*0.6):(oR/3.0);
                 })
                 .style("opacity", function(){
                         return (k==i)?1:0;
                     });
         }
     }

 window.onresize = resetBubbles;
