# Lumigator Frontend

This directory contains the **frontend** code for the **Lumigator** project, built with **Vue 3**, **Quasar**, and **Vite**. It is a modular and scalable front-end application designed to interact with the backend API provided by the Lumigator backend.

## Tech Stack

- **Vue 3**: The progressive JavaScript framework for building modern web interfaces.
- **Quasar**: A UI library for Vue.js that supports responsive designs and can be used to create websites, mobile apps, and desktop apps.
- **Vite**: A fast build tool and development server that supports modern JavaScript and hot module replacement (HMR).

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- **Node.js** (version 14 or higher)
- **npm** or **yarn** package manager

To check your installed versions:

```bash
node -v
npm -v
```

### Installation

1. **Clone the repository** (if you haven't already) and navigate to the `frontend` directory:

   ```bash
   git clone https://github.com/mozilla-ai/lumigator.git
   cd lumigator/frontend
   ```

2. **Install dependencies**:

   Using npm:

   ```bash
   npm install
   ```

   Or using yarn:

   ```bash
   yarn install
   ```

### Development

To run the frontend locally for development purposes, use the following command to start the Vite development server. This will also enable hot-reloading, so changes you make in the code will be reflected instantly in the browser.

```bash
npm run dev
```

This will run the application at `http://localhost:3000` by default.

### Build for Production

To build the frontend for production, run:

```bash
npm run build
```

This command will bundle the frontend code into a production-ready, optimized set of static assets located in the `dist` directory.

### Linting and Code Formatting

For consistent code formatting and linting across multiple contributors, ESLint and Prettier are configured. To run linting:

```bash
npm run lint
```

To fix linting issues automatically:

```bash
npm run lint:fix
```

### Directory Structure

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

### Environment Variables

To configure environment variables, create an `.env` file in the root of the `frontend` directory with the following structure:

```bash
VITE_API_URL=http://localhost:8000/api  # Backend API URL
```

You can add other environment-specific variables as needed.

### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Create a pull request.

### License

This project is licensed under the [Mozilla Public License 2.0](https://www.mozilla.org/en-US/MPL/2.0/).

```

```