// wroclaw center 51.1104/17.0317


class EmergencyAlert {
    constructor(main_app, id, start_latitude, start_longitude, additional_info, status, priority) {
        const self = this;

        self.main_app = main_app;
        self.id = id;
        self.start_latitude = start_latitude;
        self.start_longitude = start_longitude;
        self.additional_info = additional_info;
        self.status = status;
        self.priority = priority;

        self.marker = L.marker([self.start_latitude, self.start_longitude]).addTo(self.main_app.map);
    }

    update_data(data) {
        const self = this;
        console.log('Emergency Alert update data called', data);
        self.start_latitude = data.latitude;
        self.start_longitude = data.longitude;
        self.status = data.status;
        self.priority = data.priority;
        self.additional_info = data.additional_info;

        self.marker.setLatLng(new L.LatLng(self.start_latitude, self.start_longitude));
    }
}

class MainApp {
    constructor(map_id, js_lookup, test_button_id) {
        const self = this;

        self.user_groups = js_lookup['user_groups'];
        self.user_id = js_lookup['user_id'];

        self.map = self.initialize_map(map_id);

        self.emergency_alerts = [];
        self.paramedics = [];

        self.position = null;
        self.postion_marker = null;

        self.navigator_id = navigator.geolocation.watchPosition(
            function (pos) {
                self.watch_position_success(pos);
            },
            function (err) {
                self.watch_position_error(err);
            }
        );

        self.socket_connected = false;
        self.web_socket = new WebSocket(`ws://${window.location.host}/ws/base_app/`);
        self.web_socket.onopen = function (e) {
            self.socket_connected = true;
            if (self.position) {
                self.send_position(self.position);
            }
        }
        self.web_socket.onmessage = function (e) {
            let data = JSON.parse(e.data);
            console.log(data);
            if ('type' in data) {
                self.process_data(data.type, data.data);
            }
        }
        self.web_socket.onclose = function (e) {
            console.error('Web socket closed unexpectedly');
            self.socket_connected = false;
            // TODO retry connection
        }
    }

    initialize_map(map_id) {
        let map = L.map(map_id).setView([51.1104, 17.0317], 12);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        return map;
    }

    watch_position_success(pos) {
        const self = this;
        const crd = pos.coords;

        if (!self.position) {
            self.position = crd;
            self.position_marker = L.marker([self.position.latitude, self.position.longitude]).addTo(self.map);
            self.send_position(crd);
            return;
        }

        if (crd.longitude !== self.position.longitude || crd.latitude !== self.position.latitude) {
            console.log(`Position changed!!: ${crd.longitude}, ${crd.latitude}`);
            self.position = crd;
            self.position_marker.setLatLng(new L.LatLng(crd.latitude, crd.longitude));
            self.send_position(crd);
        }
    }

    watch_position_error(err) {
        alert(`ERROR location ${err.code}: ${err.message}`);
    }

    send_position(crd) {
        const self = this;
        console.log('SENDING POSITION!: ', crd);
        self.socket_send({
            type: 'position_update',
            data: {
                latitude: crd.latitude,
                longitude: crd.longitude,
                accuracy: crd.accuracy
            }
        });
    }

    socket_send(data) {
        const self = this;

        let d = {
            user_id: self.user_id,
            data: data
        }
        if (self.socket_connected) {
            self.web_socket.send(JSON.stringify(d));
        } else {
            console.error('Socket is not yet connected');
        }
    }

    process_data(_type, data) {
        const self = this;
        console.log('processing: ', _type, data);
        switch (_type) {
            case 'broadcast_emergency_alert':
                console.log('processing broadcast emergency alert');
                self.update_emergency_alert(data);
                break;
            default:
                console.log('Process Type didnt match any available methods');
        }
    }

    update_emergency_alert(data) {
        const self = this;

        let em_alert = self.emergency_alerts.find(obj => {return obj.id = data.id});
        if (!em_alert) {
            em_alert = new EmergencyAlert(self, data.id, data.latitude, data.longitude, data.additional_info, data.status, data.priority);
            self.emergency_alerts.push(em_alert);
            return;
        }
        em_alert.update_data(data);
    }
}