# Frontend-Only Manuals App (MVP)

This project is a frontend-only Minimum Viable Product (MVP) of a manual management application. It is built with React Native and Expo, and it uses the device's local storage (`AsyncStorage`) for all data persistence, requiring no backend.

## Features

-   **Add Manuals:** Create and save text-based manuals.
-   **Browse & Search:** View a list of all saved manuals and search them by title, content, or tags.
-   **QR Code Scanning:** Use the device's camera to scan a QR code and use its data to pre-fill a new manual.
-   **Offline First:** All data is stored locally on the device.

## Getting Started

### Prerequisites

-   [Node.js](https://nodejs.org/) (LTS version recommended)
-   [Visual Studio Code](https://code.visualstudio.com/) (or another code editor)
-   [Expo Go](https://expo.dev/client) app on your mobile device (iOS or Android)

### Running the Application

1.  **Navigate to the Project Directory:**
    Open your terminal and navigate to this project's folder:
    ```bash
    cd frontend_mvp/manuals-local-storage
    ```

2.  **Install Dependencies:**
    Run the following command to install all the necessary packages.
    ```bash
    npm install
    ```

3.  **Start the Expo Development Server:**
    Once the installation is complete, start the server.
    ```bash
    npm start
    ```

4.  **Run on Your Device:**
    -   The command will output a QR code in the terminal.
    -   Open the **Expo Go** app on your iOS or Android phone.
    -   Scan the QR code from the terminal. The app will begin to build and will soon open on your device.

## How It Works

-   **Data Storage:** All manual data is stored in the device's local storage using `@react-native-async-storage/async-storage`. The logic for this is encapsulated in the `app/utils/storage.js` file.
-   **Navigation:** The app uses Expo Router for file-based navigation. The main layout and tabs are defined in `app/_layout.js`.
-   **State Management:** The app uses React's built-in state management (`useState`, `useEffect`, `useCallback`) to handle the application state.
-   **First Launch:** On the very first launch, the application will seed the local storage with two sample manuals to demonstrate functionality.
