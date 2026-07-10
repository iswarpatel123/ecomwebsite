 To run individual sites in this monorepo like sites/furniture/, here are the key approaches:

 Direct Site Navigation

 Since each site is an independent pnpm workspace with its own scripts:

 ```bash
   # Navigate to the furniture site
   cd sites/furniture

   # Run the site locally
   npm run dev        # vite dev - Runs the development server
   npm run build      # vite build - Builds for production
   npm start          # vite start - Starts the built production server
   npm run preview    # vite preview - Preview the production build
 ```

 Monorepo Scripts (Turborepo)

 The root monorepo provides turborepo scripts that can target specific sites:

 ```bash
   # Run only the furniture site from the root
   npx turbo run dev --filter="@dropshipping/site-furniture"

   # Build only the furniture site from the root
   npx turbo run build --filter="@dropshipping/site-furniture"

   # Run all sites from the root
   npx turbo run dev    # Runs all sites in parallel
   npx turbo run build  # Builds all sites
 ```

 What Each Command Does

 - vite dev: Development server with hot module replacement, local API mocking, and SolidJS development features
 - vite build: Production build optimized for Cloudflare Pages deployment (generates Cloudflare Pages-compatible output)
 - vite start: Starts the statically pre-rendered site for local production testing
 - vite preview: Preview server for testing the production build locally

 Architecture Context

 From AGENTS.md:
 - Each sites/* is a "Niche-specific apps (NOT shared, custom-tailored layout/UX)"
 - Sites have "independent CI workflows" in .github/workflows/
 - All sites deploy to their own "dedicated Cloudflare Pages project"
 - The vite.config.ts in each site is configured with preset: "cloudflare-pages"

 This means you can develop, test, and deploy each niche site (furniture, saunas, etc.) completely independently without affecting other sites in the monorepo.
