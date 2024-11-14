# Frontend Quickstart

This guide can be used to build and run the Lumigator frontend (UI) for development or production environments.

## Prerequisites

Ensure you have the following installed on your system:

- **Node.js** (version 14 or higher)
- **npm** or **yarn** package manager

## Installation

1. **Clone the repository** (if you haven't already):

   Using HTTPS:

   ```console
   user@host:~$ git clone https://github.com/mozilla-ai/lumigator.git
   ```

   Or using SSH:

   ```console
   user@host:~$ git@github.com:mozilla-ai/lumigator.git
   ```

1. Navigate to the `lumigator/frontend` directory:

   ```console
   user@host:~$ cd lumigator/lumigator/frontend
   ```

1. **Install dependencies**:

   Using npm:

   ```console
   user@host:~/lumigator/lumigator/frontend$ npm install
   ```

   Or using yarn:

   ```console
   user@host:~/lumigator/lumigator/frontend$ yarn install
   ```

## Development

To run the frontend locally for development purposes, use the following command to start the Vite development server. This will also enable hot-reloading, so changes you make in the code will be reflected instantly in the browser.

```console
user@host:~/lumigator/lumigator/frontend$ npm run dev
```

Or using yarn:

```console
user@host:~/lumigator/lumigator/frontend$ yarn dev
```

Visit `http://localhost:3000` in your browser. The application runs at this address by default.

## Build for Production

To build the frontend for production, run:

```console
user@host:~/lumigator/lumigator/frontend$ npm run build
```

This command will bundle the frontend code into a production-ready, optimized set of static assets located in the `dist` directory. By default `dist` is placed in project's root directory ( `./frontend` in this case) .

## Linting and Code Formatting

For consistent code formatting and linting across multiple contributors, ESLint and Prettier are configured. To run linting:

```console
user@host:~/lumigator/lumigator/frontend$ npm run lint
```

To fix linting issues automatically:

```console
user@host:~/lumigator/lumigator/frontend$ npm run lint:fix
```

## Environment Variables

To configure environment variables, create an `.env` file in the root of the `frontend` directory with the following structure:

```bash
VUE_APP_BASE_URL=http://localhost:8000/api  # Backend API URL
```

You can add other environment-specific variables as needed.
