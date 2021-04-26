function(doc) {
    if (doc.coordinates != null) {
      index('lon_min', doc.coordinates.coordinates[0], {'store': true});
      index('lon_max', doc.coordinates.coordinates[0], {'store': true});
      index('lat_min', doc.coordinates.coordinates[1], {'store': true});
      index('lat_max', doc.coordinates.coordinates[1], {'store': true});
    } else if (doc.place != null) {
      lon1 = doc.place.bounding_box.coordinates[0][0][0];
      lat1 = doc.place.bounding_box.coordinates[0][0][1];
      lon2 = doc.place.bounding_box.coordinates[0][1][0];
      lat2 = doc.place.bounding_box.coordinates[0][1][1];
      lon3 = doc.place.bounding_box.coordinates[0][2][0];
      lat3 = doc.place.bounding_box.coordinates[0][2][1];
      lon4 = doc.place.bounding_box.coordinates[0][3][0];
      lat4 = doc.place.bounding_box.coordinates[0][3][1];
      
      index('lon_min', Math.min(lon1, lon2, lon3, lon4), {'store': true});
      index('lon_max', Math.max(lon1, lon2, lon3, lon4), {'store': true});
      index('lat_min', Math.min(lat1, lat2, lat3, lat4), {'store': true});
      index('lat_max', Math.max(lat1, lat2, lat3, lat4), {'store': true});
    }
  }