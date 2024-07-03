import "@mantine/core/styles.css";

import {
  Container,
  createTheme,
  List,
  MantineProvider,
  Title,
} from "@mantine/core";
import { useState } from "react";

const theme = createTheme({});

export function ResultsPage({ assistantId }: { assistantId: string }) {
    const [lat, setLat] = useState(0);
    const [lon, setLon] = useState(0);
    const successCallback = (position) => {
        console.log(position);
        setLat(position.coords.latitude);
        setLon(position.coords.longitude);
    };
    
    const errorCallback = (error) => {
        console.log(error);
    };
      
    navigator.geolocation.getCurrentPosition(successCallback, errorCallback);
    return (
        <Container>
        hi
        lat: {lat}
        lon: {lon}
        </Container>
    );
};

