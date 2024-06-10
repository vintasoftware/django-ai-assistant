import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "openapi_schema.json",
  output: "src/client",
  client: "axios",
  useOptions: true,
});
