# React Native Manuals App

This project is a conversion of a Streamlit application into a React Native mobile app with a Flask backend.

## Project Structure

-   `/react_native_app/backend`: The Python Flask API server.
-   `/react_native_app/frontend`: The React Native (Expo) mobile application.
-   The original Streamlit files are preserved in the root directory.

## Prerequisites

-   [Node.js](https://nodejs.org/) (LTS version recommended)
-   [Python](https://www.python.org/downloads/) (3.8 or higher)
-   [Visual Studio Code](https://code.visualstudio.com/)
-   [Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
-   [React Native Tools extension for VS Code](https://marketplace.visualstudio.com/items?itemName=msjsdiag.vscode-react-native) (optional but recommended)
-   [Expo Go](https://expo.dev/client) app on your mobile device (iOS or Android)

---

## Running the Backend (Flask) in Debug Mode

1.  **Open the Backend Folder in VS Code:**
    -   Open Visual Studio Code.
    -   Go to `File > Open Folder...` and select the `react_native_app/backend` directory.

2.  **Set up the Python Environment:**
    -   Open a new terminal in VS Code (`Terminal > New Terminal`).
    -   Create a virtual environment:
        ```bash
        python -m venv .venv
        ```
    -   Activate the virtual environment:
        -   On macOS/Linux: `source .venv/bin/activate`
        -   On Windows: `.venv\Scripts\activate`
    -   Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Create the Debug Configuration (`launch.json`):**
    -   Click on the **Run and Debug** icon in the Activity Bar on the side of VS Code (or press `Ctrl+Shift+D`).
    -   Click on the "create a launch.json file" link.
    -   Select **Flask** from the dropdown menu. VS Code will generate a `launch.json` file inside a `.vscode` directory.
    -   Replace the contents of the generated `launch.json` with the following configuration. This ensures it points to our specific app file.

    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Flask",
                "type": "python",
                "request": "launch",
                "module": "flask",
                "env": {
                    "FLASK_APP": "app.py",
                    "FLASK_DEBUG": "1"
                    // If you are using a PostgreSQL database, add your DATABASE_URL here
                    // "DATABASE_URL": "postgresql://user:password@host:port/database"
                },
                "args": [
                    "run",
                    "--no-debugger"
                ],
                "jinja": true,
                "justMyCode": true
            }
        ]
    }
    ```

4.  **Start Debugging:**
    -   Go back to the **Run and Debug** view.
    -   Make sure "Python: Flask" is selected in the dropdown menu at the top.
    -   Press the green play button (or `F5`) to start the debugger.
    -   The Flask server will start, and you can now set breakpoints in your Python code. The terminal will show the server running on `http://127.0.0.1:5000`.

---

## Running the Frontend (React Native) in Debug Mode

1.  **Open the Frontend Folder in VS Code:**
    -   Open a new VS Code window.
    -   Go to `File > Open Folder...` and select the `react_native_app/frontend` directory.

2.  **Install Dependencies:**
    -   Open a new terminal in VS Code.
    -   Install the project dependencies:
        ```bash
        npm install
        ```

3.  **Update the API URL:**
    -   Open the file `app/index.js`.
    -   Find the `API_URL` constant.
    -   Replace the placeholder IP address with the local IP address of the computer running the backend server. For example: `http://192.168.1.100:5000/api`.
        -   You can find your local IP on macOS/Linux with `ifconfig` or `ip a`, and on Windows with `ipconfig`.

4.  **Create the Debug Configuration (`launch.json`):**
    -   Click on the **Run and Debug** icon.
    -   Click on "create a launch.json file".
    -   Select **React Native** from the dropdown.
    -   Choose "Attach to application" as the debug configuration.
    -   VS Code will generate a `launch.json` file. You can usually use the default configuration for attaching. It should look something like this:

    ```json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Attach to application",
                "request": "attach",
                "type": "reactnative",
                "cwd": "${workspaceFolder}"
            }
        ]
    }
    ```

5.  **Start the App and the Debugger:**
    -   In the VS Code terminal, start the Expo development server:
        ```bash
        npm start
        ```
    -   A QR code will appear in the terminal. Scan this QR code with the **Expo Go** app on your phone.
    -   Once the app is running on your phone, go to the **Run and Debug** view in VS Code.
    -   Make sure "Attach to application" is selected, and press the green play button (`F5`).
    -   The debugger will attach to your app. You can now set breakpoints in your JavaScript/TypeScript code and use the debug console.
