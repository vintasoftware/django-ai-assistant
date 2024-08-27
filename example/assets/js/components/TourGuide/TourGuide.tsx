import "@mantine/core/styles.css";
import { Container, TextInput, Button } from "@mantine/core";
import { useEffect, useState } from "react";
import classes from "./TourGuide.module.css";

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
      <div className={classes.searchBar}>
        <span className={classes.inputBlock}>
          Latitude:
          <TextInput
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            className={classes.coordinateInput}
          />
        </span>
        <span className={classes.inputBlock}>
          Longitude:
          <TextInput
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            className={classes.coordinateInput}
          />
        </span>
        <Button className={classes.inputBlock} onClick={findAttractions}>
          Guide Me!
        </Button>
      </div>
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
