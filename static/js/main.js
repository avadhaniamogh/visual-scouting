queue()
    .defer(d3.json, "/data/menu/")
    .await(initMenu);

function init(error, standings) {

    for (var key in standings) {
        console.log(key);
        console.log(standings[key]);
    }

    loadStackedBars();


}
