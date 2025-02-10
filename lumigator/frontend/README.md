# Lumigator Frontend

This directory contains the **frontend** code for the **Lumigator** project, built with **Vue 3**, and **Vite**. It is a modular and scalable front-end application designed to interact with the backend API provided by the Lumigator backend.

## Tech Stack

- **Vue 3**: The progressive JavaScript framework for building modern web interfaces.
- **Vite**: A fast build tool and development server that supports modern JavaScript and hot module replacement (HMR).

## Directory Structure

```plaintext
frontend/
├── public/              # Static assets
├── src/
│   ├── api/             # API services
│   ├── assets/          # Images, fonts, and other assets
│   ├── components/      # Reusable Vue components
│   ├── layouts/         # Page layouts
│   ├── pages/           # Views and pages
│   ├── router/          # Vue Router setup
│   ├── store/           # Pinia store setup
│   ├── styles/          # Global styles, including Quasar variables
│   ├── App.vue          # Main Vue component
│   └── main.js          # Application entry point
├── index.html           # HTML entry point
├── package.json         # Project configuration and dependencies
├── vite.config.js       # Vite configuration
└── README.md            # Frontend README file (this file)
```


## Running the project
- You can start the project by running `yarn dev` or `npm run-script dev`

## Unit testing
- To run unit tests you can run `yarn test:unit` or `npm run-script test:unit`

## E2E testing
- To run e2e tests you can run `yarn test:e2e` or `npm run-script test:e2e`
