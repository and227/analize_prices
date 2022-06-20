google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    const axios_inst = axios.create({
        baseURL: 'http://localhost:8080',
        timeout: 1000,
    });

    let prices = axios_inst.get("/prices")
        .then(function(response) {
          let dataToInsert = response.data.map(item => Object.values(item));
          let data = google.visualization.arrayToDataTable(dataToInsert, true);
          let options = {
            legend:'none'
          };
          let chart = new google.visualization.CandlestickChart(document.getElementById('chart_div'));
          chart.draw(data, options);
        })
        .catch(function(error) {
          console.log(error)
        })
}