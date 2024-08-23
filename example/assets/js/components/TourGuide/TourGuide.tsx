import "@mantine/core/styles.css";
import { Container } from "@mantine/core";
import axios from 'axios';
import { useEffect, useState } from "react";


export function TourGuide() {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [attractions, setAttractions] = useState([]);
  const [loading, setLoading] = useState(false);

  navigator.geolocation.getCurrentPosition((position: any) => {
    if (latitude && longitude) {
      return;
    }
    setLatitude(position.coords.latitude);
    setLongitude(position.coords.longitude);
  }, (error) => console.log(error));

  function findAttractions() {
    if (!latitude || !longitude) {
      return;
    }

    setLoading(true)
    axios.get(`/tour-guide/?coordinate=${latitude},${longitude}`)
      .then((response: any) => {
        setAttractions(response.data.nearby_attractions)
      }).finally(() => setLoading(false))
  }

  console.log(attractions)

  return (
    <Container>
      Latitude: <input type="text" value={latitude} onChange={(e) => setLatitude(e.target.value)} />
      Longitude: <input type="text" value={longitude} onChange={(e) => setLongitude(e.target.value)} />
      <button onClick={findAttractions}>Guide Me!</button>
      {loading ? <h3>Loading</h3> : null}
      <div>
        {attractions.map((item, i) =>
          <div key={i}>
            <h2>{item.attraction_url ? <a href={item.attraction_url}>{item.attraction_name}</a> : item.attraction_name }</h2>
            <span>{item.attraction_description}</span>

          </div>
        )}
      </div>
    </Container>
  );
};

