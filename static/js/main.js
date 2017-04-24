queue()
    .defer(d3.json, "/data/countries/teams?country_id=1729")
    .await(init);

function init(error, standings) {

    // for (var key in standings) {
    //     console.log(key);
    //     console.log(standings[key]);
    // }


}