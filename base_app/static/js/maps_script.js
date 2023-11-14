// wroclaw center 51.1104/17.0317
    var map = L.map('map').setView([51.1104, 17.0317], 12);
    var previous_position = null;
    let marker = null;

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition);
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    }

    function watchPositionSuccess(pos) {
        const crd = pos.coords;
        if (!previous_position) {
            previous_position = crd;

        }

        if (crd.longitude !== previous_position.longitude || crd.latitude !== previous_position.latitude) {
            alert(`Position changed!!: ${crd.longitude}, ${crd.latitude}`);
            previous_position = crd;
            marker.setLatLng(new L.LatLng(crd.latitude, crd.longitude));
        }
    }

    function watchPositionError(err) {
        alert(`ERROR location ${err.code}: ${err.message}`);
    }

    function showPosition(position) {
        previous_position = position.coords;
        let msg = "Latitude: " + position.coords.latitude +
            "<br>Longitude: " + position.coords.longitude;
        marker = L.marker([position.coords.latitude, position.coords.longitude]).addTo(map);
        alert(msg);
        marker.bindPopup(msg);
    }

    $(document).ready(function (e) {
        getLocation();

        let id = navigator.geolocation.watchPosition(watchPositionSuccess, watchPositionError);

        const socket = new WebSocket(`ws://${window.location.host}/ws/base_app/`);
        socket.onmessage = function (e) {
            let data = JSON.parse(e.data);
            console.log(data);
        }
    });