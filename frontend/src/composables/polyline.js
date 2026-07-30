import L from 'leaflet'

// Dekodiert den komprimierten String zurück in ein [Lat, Lng] Array
export const decodePolyline = (encoded) => {
    const coordinates = [];
    let index = 0, len = encoded.length;
    let lat = 0, lng = 0;

    while (index < len) {
        let b, shift = 0, result = 0;
        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);
        let dlat = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1));
        lat += dlat;

        shift = 0;
        result = 0;
        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);
        let dlng = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1));
        lng += dlng;

        coordinates.push([lat / 1e5, lng / 1e5]);
    }
    return coordinates;
};

// Summiert die Punktabstände einer Koordinatenliste in Metern
export const calculateRouteDistance = (coordinates) => {
    let distance = 0;
    for (let i = 1; i < coordinates.length; i++) {
        distance += L.latLng(coordinates[i - 1]).distanceTo(L.latLng(coordinates[i]));
    }
    return distance;
};
