import "@mantine/core/styles.css";
import {
  Container,
  TextInput,
  Button,
  LoadingOverlay,
  Group,
} from "@mantine/core";
import { useEffect, useState } from "react";

export function TourGuide() {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [attractions, setAttractions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position: any) => {
        setLatitude(position.coords.latitude);
        setLongitude(position.coords.longitude);
      },
      (error) => console.log(error)
    );
  }, []);

  function findAttractions() {
    if (!latitude || !longitude) {
      return;
    }

    setLoading(true);
    fetch(`/tour-guide/?coordinate=${latitude},${longitude}`)
      .then((response) => response.json())
      .then((data: any) => {
        console.log(data);

        setAttractions(data.nearby_attractions);
      })
      .finally(() => setLoading(false));
  }

  return (
    <Container>
      <LoadingOverlay visible={loading} />
      <Group justify="left" align="flex-end">
        <TextInput
          required
          label="Latitude"
          value={latitude}
          onChange={(e) => setLatitude(e.target.value)}
        />
        <TextInput
          required
          label="Longitude"
          value={longitude}
          onChange={(e) => setLongitude(e.target.value)}
        />
        <Button onClick={findAttractions}>Guide Me!</Button>
      </Group>
      {loading ? <h3>Loading</h3> : null}
      <div>
        {attractions.map((item, i) => (
          <div key={i}>
            <h2>
              {item.attraction_url ? (
                <a href={item.attraction_url} target="_blank">
                  {item.attraction_name}
                </a>
              ) : (
                item.attraction_name
              )}
            </h2>
            <span>{item.attraction_description}</span>
            <div>
              <a
                href={`https://www.google.com/maps?q=${item.attraction_name}`}
                target="_blank"
              >
                Open in Google Maps
              </a>
            </div>
          </div>
        ))}
      </div>
    </Container>
  );
}
