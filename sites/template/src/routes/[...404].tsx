import { MetaProvider } from "@solidjs/meta";
import { A } from "@solidjs/router";

export default function NotFound() {
  return (
    <MetaProvider>
      <main class="min-h-screen flex items-center justify-center">
        <div class="text-center">
          <h1 class="text-6xl font-bold">404</h1>
          <p class="mt-4 text-xl">Page not found</p>
          <A href="/" class="mt-8 inline-block text-blue-600 hover:underline">
            Go home
          </A>
        </div>
      </main>
    </MetaProvider>
  );
}