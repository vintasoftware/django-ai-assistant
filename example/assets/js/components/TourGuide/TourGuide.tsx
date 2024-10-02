import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Button,
  Card,
  Container,
  Flex,
  Group,
  LoadingOverlay,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconLocation, IconMap2 } from "@tabler/icons-react";

interface Attraction {
  name: string;
  description: string;
  url: string;
}

export function TourGuide() {
  const [showLoginNotification, setShowLoginNotification] =
    useState<boolean>(false);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [attractions, setAttractions] = useState<Attraction[]>([]);
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
    const response = await fetch(
      `/tour-guide/?coordinate=${latitude},${longitude}`
    );
    const data = await response.json();
    if (data.error) {
      setShowLoginNotification(true);
    } else {
      setAttractions(data.nearby_attractions);
    }
    setLoading(false);
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

      <Title mt="md" order={2}>
        Tour Guide
      </Title>

      <Group justify="left" align="flex-end" mb="xl">
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
        <Button
          leftSection={<IconMap2 size={18} stroke={1.5} />}
          onClick={findAttractions}
        >
          Guide Me!
        </Button>
      </Group>

      <Flex gap="md" align="flex-start" direction="row" wrap="wrap" miw={460}>
        {attractions.map((attraction, index) => (
          <Card
            key={index}
            w={280}
            shadow="sm"
            padding="lg"
            radius="md"
            withBorder
          >
            <Text fw={500} size="lg" mt="md" mb="xs">
              {attraction.name}
            </Text>
            <Text size="sm" c="dimmed" mb="md">
              {attraction.description}
            </Text>
            <Button
              component="a"
              href={`https://www.google.com/maps/search/?api=1&query=${attraction.name}`}
              target="_blank"
              rel="noopener noreferrer"
              variant="light"
              leftSection={<IconLocation size={18} stroke={1.5} />}
            >
              View on Google Maps
            </Button>
          </Card>
        ))}
      </Flex>
    </Container>
  );
}
