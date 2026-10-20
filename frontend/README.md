# FlowOS web client placeholder

The planned client stack is React, TypeScript, and Vite. No packages are installed and no product UI is implemented in V0.1 project initialization.

Planned structure:

```text
src/
  app/         application shell, routing, providers
  features/    order lookup, inventory gaps, purchase draft workflows
  components/  shared presentation components
  api/         typed HTTP client and API contracts
  styles/      design tokens and global styles
```

When frontend implementation starts, initialize Vite directly in this directory and keep backend-generated or manually maintained API types isolated under `src/api`. All fixtures and demos must use synthetic data only.

