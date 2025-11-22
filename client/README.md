<div align="center">
  <img width="100%" src="./assets/CivicFlow_Banner.png" alt="Civic Flow Banner" />

  # Civic Flow
  ### AI-Powered Civic Engagement Platform

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
  [![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)](https://reactjs.org/)
  [![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
  [![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

  <p align="center">
    <b>Civic Flow</b> empowers citizens to engage with policy through intelligent, AI-driven conversations.
    <br />
    <a href="https://ai.studio/apps/temp/1"><strong>View Demo »</strong></a>
    <br />
    <br />
    <a href="#-getting-started">Getting Started</a>
    ·
    <a href="#-features">Features</a>
    ·
    <a href="#-tech-stack">Tech Stack</a>
  </p>
</div>

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### 📋 Prerequisites

Ensure you have the following installed on your system:

*   **[Docker Desktop](https://www.docker.com/products/docker-desktop)** (includes Docker Compose)
*   **[Node.js](https://nodejs.org/)** (v18+ recommended) - *Optional if running via Docker*

### 🐳 Running with Docker (Recommended)

We use Docker Compose to streamline the setup process. This will build the client image and start the application.

#### 1. Build the Image

Navigate to the project root (where `docker-compose.yaml` is located) and run:

```bash
docker-compose build
```

#### 2. Run the Project

Start the services in detached mode:

```bash
docker-compose up -d
```

The application should now be accessible at `http://localhost:3000` (or the port configured in your docker-compose).

> **Note:** To stop the containers, run `docker-compose down`.

### 💻 Running Locally (Manual Setup)

If you prefer to run the application without Docker:

1.  **Install Dependencies**

    Navigate to the `client` directory and install the required packages:

    ```bash
    cd client
    npm install
    ```

2.  **Configure Environment**

    Create a `.env.local` file in the `client` directory and add your Gemini API key:

    ```env
    VITE_GEMINI_API_KEY=your_api_key_here
    ```

3.  **Start Development Server**

    ```bash
    npm run dev
    ```

    Open your browser and navigate to the URL shown in the terminal (usually `http://localhost:5173`).

---

## ✨ Features

*   **🤖 AI Policy Chat:** Interact with an intelligent assistant to understand complex civic policies.
*   **🔔 Real-time Notifications:** Stay updated with the latest changes and alerts.
*   **📱 Responsive Design:** Seamless experience across desktop and mobile devices.
*   **⚡ Blazing Fast:** Built with Vite for instant server start and hot module replacement.

## 🛠️ Tech Stack

*   **Frontend:** React, TypeScript, Vite
*   **Styling:** Tailwind CSS, Lucide React
*   **AI Integration:** Google Gemini API
*   **Testing:** Jest, React Testing Library
*   **Containerization:** Docker

---

<div align="center">
  <sub>Built with ❤️ by the Civic Flow Team</sub>
</div>
