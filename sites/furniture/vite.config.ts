import { defineConfig } from "vite";
import { nitroV2Plugin as nitro } from "@solidjs/vite-plugin-nitro-2";
import { solidStart } from "@solidjs/start/config";

// Ports via package.json scripts (--port/--host/--strictPort).
// SSG: Nitro `static` + prerender → pure CF Pages assets (no Functions).
export default defineConfig({
  plugins: [
    solidStart(),
    nitro({
      preset: "static",
      prerender: {
        crawlLinks: true,
        routes: ["/", "/collections"]
      }
    })
  ],
  server: {
    allowedHosts: [
      "3001-01kxkp3hnqf6pxk9jsv9v6ct9j.cloudspaces.litng.ai"
    ]
  }
});
