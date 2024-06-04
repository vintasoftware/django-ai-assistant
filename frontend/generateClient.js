#!/usr/bin/env node

import { createClient } from "@hey-api/openapi-ts";
import { Command } from "commander";
import path from "path";
import fs from "fs";

const program = new Command();

async function generateClient(inputPath, outputPath) {
  return await createClient({
    input: inputPath,
    output: outputPath,
    client: "axios",
    useOptions: true,
  });
}

program
  .description("Generate a client from an OpenAPI schema")
  .argument("<inputPath>", "Path to the OpenAPI schema")
  .argument("<outputPath>", "Path to the output directory")
  .action((inputPath, outputPath) => {
    const fullInputPath = path.resolve(inputPath);
    const fullOutputPath = path.resolve(outputPath);


    if (!fs.existsSync(fullInputPath)) {
      console.error(`Schema file does not exist at path: ${fullInputPath}`);
      process.exit(1);
    }

    generateClient(fullInputPath, fullOutputPath).catch((error) => {
      console.error("Error generating client:", error);
      process.exit(1);
    });
  });

program.parse(process.argv);
