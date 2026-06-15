// Initialize the map centered on North East Nigeria
var map = L.map('map').setView([11.5, 13.0], 7);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fetch the processed GeoJSON data
// Note: Path is relative to the location of index.html
fetch('bay_schools.geojson')
    .then(response => response.json())
    .then(data => {
        // Calculate and update KPI boxes
        const total = data.features.length;
        const highRisk = data.features.filter(f => f.properties.vulnerability_score === 'High').length;
        const percentage = total > 0 ? ((highRisk / total) * 100).toFixed(1) : 0;

        document.getElementById('total-schools').innerText = total.toLocaleString();
        document.getElementById('high-risk-schools').innerText = highRisk.toLocaleString();
        document.getElementById('disruption-percentage').innerText = percentage + '%';

        // Add the data to the map with custom styling
        L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                // Determine color based on vulnerability_score
                var color = feature.properties.vulnerability_score === 'High' ? '#ef4444' : '#22c55e';
                
                return L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: color,
                    color: "#fff",
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                });
            },
            onEachFeature: function (feature, layer) {
                // Add popup with school name and vulnerability status
                var popupContent = "<strong>School:</strong> " + (feature.properties.school_name || "Unknown") +
                                 "<br><strong>Status:</strong> " + feature.properties.vulnerability_score + " Risk";
                layer.bindPopup(popupContent);
            }
        }).addTo(map);
    })
    .catch(error => {
        console.error('Error loading the GeoJSON data:', error);
    });
