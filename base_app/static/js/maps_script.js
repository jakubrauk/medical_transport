// wroclaw center 51.1104/17.0317


class EmergencyAlert {
    constructor(main_app, id, start_latitude, start_longitude, additional_info, status, priority, paramedic_id) {
        const self = this;

        self.main_app = main_app;
        self.id = id;
        self.start_latitude = start_latitude;
        self.start_longitude = start_longitude;
        self.additional_info = additional_info;
        self.status = status;
        self.priority = priority;
        self.paramedic_id = paramedic_id;

        self.accept_button = $('<button>').addClass('btn btn-success btn-sm').text('Przyjmij zgłoszenie');
        self.finish_button = $('<button>').addClass('btn btn-danger btn-sm').text('Zakończ zgłoszenie');

        self.popup_initialized = false;

        self.marker = L.marker([self.start_latitude, self.start_longitude], {icon: self.get_marker_icon()}).addTo(self.main_app.map);
        self.popup = self.marker.bindPopup(`<div id="popup_${self.id}" style="min-width: 80px;"></div>`).on('popupopen', function (e) {
            self.set_popup_content();
        });
    }

    remove_marker() {
        const self = this;
        self.main_app.map.removeLayer(self.marker);
    }

    update_data(data) {
        const self = this;
        console.log('Emergency Alert update data called', data);
        self.start_latitude = data.latitude;
        self.start_longitude = data.longitude;
        self.status = data.status;
        self.priority = data.priority;
        self.additional_info = data.additional_info;
        self.paramedic_id = data.paramedic_id;

        self.marker.setLatLng(new L.LatLng(self.start_latitude, self.start_longitude));
        self.marker.setIcon(self.get_marker_icon());
    }

    get_marker_icon() {
        const self = this;
        return L.AwesomeMarkers.icon({
            icon: 'heart-pulse',
            markerColor: ((self.status === 'Pending') ? 'red' : 'green'),
            prefix: 'bi'
        });
    }

    set_popup_content() {
        const self = this;

        if (!self.popup_initialized) {
            self.accept_button.click(function (e) {
                self.accept_button_action();
                self.popup.closePopup();
            });
            self.finish_button.click(function (e) {
                self.finish_button_action();
                self.popup.closePopup();
            })
        }

        let popup = $(`#popup_${self.id}`);

        self.popup_initialized = true;

         popup
             .append($('<p>')
                 .append($('<b>').text(self.additional_info)));

        if (self.main_app.user_paramedic) {
            if (self.main_app.user_paramedic.status === 'FREE') {
                popup.append(self.accept_button);
            } else {
                if (self.main_app.user_paramedic.id === self.paramedic_id) {
                    popup.append(self.finish_button);
                } else {
                    popup.append($('<p>').text("Dokończ poprzednie zgłoszenie zanim rozpoczniesz kolejne!"));
                }
            }
        } else {
            popup.append($('<p>').text("Nie jesteś ratownikiem chujku, nie mozesz tego przyjac"));
        }
    }

    accept_button_action() {
        const self = this;
        console.log('accept button action');
        self.main_app.emergency_alert_accept_button(self);
    }

    finish_button_action() {
        const self = this;
        console.log('finish button action');
        self.main_app.emergency_alert_finish_button(self);
    }
}

class Paramedic {
    constructor(main_app, id, user_id, latitude, longitude, status) {
        const self = this;

        self.main_app = main_app;
        self.id = id;
        self.user_id = user_id;
        self.latitude = latitude;
        self.longitude = longitude;
        self.status = status;

        let blueMarker =

        self.marker = L.marker([self.latitude, self.longitude], {icon: self.get_marker_icon()}).addTo(self.main_app.map);
    }

    update_data(data) {
        const self = this;
        self.latitude = data.latitude;
        self.longitude = data.longitude;
        self.status = data.status;

        self.marker.setLatLng(new L.LatLng(self.latitude, self.longitude));
        self.marker.setIcon(self.get_marker_icon());
    }

    get_marker_icon() {
        const self = this;

        return L.AwesomeMarkers.icon({
            icon: ((self.status === 'IN_PROCESS') ? 'person-walking' : 'person-raised-hand'),
            markerColor: ((self.status === 'IN_PROCESS') ? 'red' : 'blue'),
            prefix: 'bi'
        });
    }
}

class MainApp {
    constructor(map_id, js_lookup, test_button_id) {
        const self = this;

        self.user_groups = js_lookup['user_groups'];
        self.user_id = js_lookup['user_id'];
        self.user_paramedic = null;  // User using app instance - paramedic
        self.directions = null;
        self.test_button_id = test_button_id;

        $('#' + test_button_id).click(function (e) {
            console.log('test button clicked');
            self.socket_send({
                type: 'test_button',
                data: {
                    message: 'HELLO'
                }
            });
        });

        self.map = self.initialize_map(map_id);

        self.emergency_alerts = [];
        self.paramedics = [];

        self.position = null;
        self.postion_marker = null;

        if (self.user_groups.includes('paramedics')) {
            self.navigator_id = navigator.geolocation.watchPosition(
                function (pos) {
                    self.watch_position_success(pos);
                },
                function (err) {
                    self.watch_position_error(err);
                }
            );
        }

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

    load_initial_data(data) {
        const self = this;
        for (let paramedic of data['paramedics']) {
            self.update_paramedic(paramedic);
        }
        for (let dispositor of data['dispositors']) {
            console.log('todo update dispositors');
        }
        for (let emergency_alert of data['emergency_alerts']) {
            self.update_emergency_alert(emergency_alert);
        }
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

    emergency_alert_accept_button(emergency_alert) {
        const self = this;
        if (self.user_paramedic) {
            self.socket_send({
                type: 'emergency_alert_accept',
                data: {
                    paramedic_id: self.user_paramedic.id,
                    emergency_alert_id: emergency_alert.id,
                }
            });
        } else {
            alert("USER ACCEPTING IS NOT A PARAMEDIC!");
        }
    }

    emergency_alert_finish_button(emergency_alert) {
        const self = this;
        if (self.user_paramedic) {
            self.socket_send({
                type: 'emergency_alert_finish',
                data: {
                    paramedic_id: self.user_paramedic.id,
                    emergency_alert_id: emergency_alert.id,
                }
            });
        } else {
            alert("USER FINISHING ALERT IS NOT A PARAMEDIC!");
        }
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
            case 'load_initial_data':
                console.log('processing load initial data');
                self.load_initial_data(data);
                break;
            case 'broadcast_emergency_alert':
                console.log('processing broadcast emergency alert');
                self.update_emergency_alert(data);
                break;
            case 'paramedic_update':
                console.log('processing broadcast paramedic update');
                self.update_paramedic(data);
                break;
            case 'emergency_alert_directions':
                self.show_directions(data);
                break;
            default:
                console.log('Process Type didnt match any available methods');
        }
    }

    update_emergency_alert(data) {
        const self = this;

        let em_alert = self.emergency_alerts.find(obj => {return obj.id === data.id});
        if (!em_alert) {
            em_alert = new EmergencyAlert(self, data.id, data.latitude, data.longitude, data.additional_info, data.status, data.priority, data.paramedic_id);
            self.emergency_alerts.push(em_alert);
            return;
        }
        em_alert.update_data(data);
        if (em_alert.status === 'Done') {
            // remove marker, remove alert from list
            em_alert.remove_marker();
            self.emergency_alerts = self.emergency_alerts.filter(item => item !== em_alert);
            console.log(self);
        }
    }

    update_paramedic(data) {
        const self = this;

        let paramedic = self.paramedics.find(obj => {return obj.id === data.id});
        if (self.user_groups)
        if (!paramedic) {
            paramedic = new Paramedic(self, data.id, data.user_id, data.latitude, data.longitude, data.status);
            self.paramedics.push(paramedic);
            return;
        }
        if (!self.user_paramedic && self.user_id === paramedic.user_id) {
            self.user_paramedic = paramedic;
        }
        paramedic.update_data(data);
        if (self.user_paramedic) {
            if (self.user_paramedic.status === 'FREE' && self.directions) {
                self.map.removeLayer(self.directions);
            }
        }
    }

    show_directions(coordinates) {
        const self = this;

        self.directions = L.polyline(coordinates, {color: 'red'}).addTo(self.map);
    }
}