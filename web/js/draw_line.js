var activeLines = [];
        function DrawLines(lines) {
            for(let i=0; i<activeLines.length; i++) {
                map.removeLayer(activeLines[i]);
            }
            for(let i=0; i<lines.length; i++) {
                const lat1 = lines[i][0];
                const long1 = lines[i][1];
                const lat2 = lines[i][2];
                const long2 = lines[i][3];

                // Define the coordinates of your points
                const pointA = L.latLng(lat1, long1);
                const pointB = L.latLng(lat2, long2);
                // Create an array of coordinates for the path
                const pathCoordinates = [pointA, pointB];

                // Create a Polyline using the path coordinates
                const polyline = L.polyline(pathCoordinates, {color: 'red', weight: 5}).addTo(map);
                const polyline1 = L.polyline(pathCoordinates, {color: 'blue', weight: 2}).addTo(map);

                activeLines.push(polyline);
                activeLines.push(polyline1);
                // Fit the map to the bounds of the polyline
                //map.fitBounds(polyline.getBounds());
            }
        }

        eel.expose(DrawLines);
