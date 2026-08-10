import L from 'leaflet'

// Dekodiert den komprimierten String zurück in ein [Lat, Lng] Array
// Google Encoded Polyline Algorithm Format (Gegenstück zu encodePolyline in
// useGPXVerarbeitung.js) - in diesem Format liefert auch Strava seine Routen.
export const decodePolyline = (encoded) => {
    const coordinates = [];
    let index = 0, len = encoded.length;
    let lat = 0, lng = 0;

    while (index < len) {
        let b, shift = 0, result = 0;
        do {
            // -63 kehrt den ASCII-Offset des Encoders um; b >= 0x20 (Bit 6 gesetzt)
            // zeigt an, dass noch ein weiterer 5-Bit-Block zu diesem Wert gehört
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);
        // Zickzack-Dekodierung: Vorzeichen steckt im niedrigsten Bit von result
        let dlat = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1));
        lat += dlat; // Werte sind Deltas zum vorherigen Punkt, keine Absolutkoordinaten

        shift = 0;
        result = 0;
        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);
        let dlng = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1));
        lng += dlng;

        coordinates.push([lat / 1e5, lng / 1e5]); // Format ist mit 5 Nachkommastellen Genauigkeit kodiert
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
