import "@mantine/core/styles.css";
import {
  Container,
  TextInput,
  Button,
  LoadingOverlay,
  Group,
} from "@mantine/core";
import { useEffect, useState } from "react";
import { notifications } from "@mantine/notifications";
import { Link } from "react-router-dom";

export function TourGuide() {
  const [showLoginNotification, setShowLoginNotification] =
    useState<boolean>(false);
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

  async function findAttractions() {
    if (!latitude || !longitude) {
      return;
    }

    setLoading(true);
    const response = await fetch(`/tour-guide/?coordinate=${latitude},${longitude}`);
    const data = await response.json();
    if (data.error) {
      setShowLoginNotification(true);
    } else {
      setAttractions(data.nearby_attractions);
    }
    setLoading(false)
  }

  useEffect(() => {
    if (!showLoginNotification) return;

    notifications.show({
      title: "Login Required",
      message: (
        <>
          You must be logged in to engage with the examples. Please{" "}
          <Link to="/admin/" target="_blank">
            log in
          </Link>{" "}
          to continue.
        </>
      ),
      color: "red",
      autoClose: 5000,
      withCloseButton: true,
    });
  }, [showLoginNotification]);

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
