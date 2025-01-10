# WikiKuvaVisa

**WikiKuvaVisa** is a web-based quiz application that challenges users to identify the correct title of a Finnish Wikipedia page based on a displayed image. The application uses the Wikimedia API for fetching content and is built with Python and Flask. The user selects one of three options, and the result page provides feedback, a link to the correct Wikipedia page, and a brief explanation.

## Features
- Fetches random pages with images from Finnish Wikipedia.
- Displays three title options, one of which is correct.
- Measures the time taken for a user to make a guess.
- Gradually reveals the quiz image from blurred to clear over 10 seconds.
- Provides feedback, the correct title, and a link with a summary on the result page.

## Technologies Used
- **Python** for server-side logic.
- **Flask** as the web framework.
- **Wikimedia API** for fetching Wikipedia content.
- **Base64 encoding** to obfuscate the correct answer.
- **Docker** for containerized deployment.
- **Kubernetes** for scalability and service management.

## Installation

### Prerequisites
- Python 3.8+
- Docker and Docker Compose
- Kubernetes (optional, for production)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/emehtata/wikikuvavisa.git
   cd wikikuvavisa
   ```
2. Create a `keys.json` file in `app/` with your details (see `key.json.example`):
   ```json
    {
        "appid": "your_application_name",
        "userid": "your_email_address_or_url"
    }
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application locally:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5500`.

## Docker Usage

### Build and Run the Container
1. Build the Docker image:
   ```bash
   make build
   ```
1. Run the container:
   ```bash
   make run
   ```
   The app will be available at `http://localhost:5500`.
1. Stop and remove the container:
   ```bash
   make stop rm
   ```

### Using the Makefile
The provided `Makefile` simplifies container management:
- Build and push the image:
  ```bash
  make build
  make push
  ```
- Stop and remove the container:
  ```bash
  make stop
  make rm
  ```

## Kubernetes Deployment

### Deployment and Service Configuration

Apply the helm deployment chart:
   ```bash
   make install
   ```

Uninstall:
   ```bash
   make uninstall
   ```

## Makefile

See `Makefile` for more targets.

## Future Improvements
- Enhance error handling and logging.
- Implement category-based option selection to improve quiz relevance.
- Add internationalization support for other languages.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with improvements or bug fixes.

## Author
[emehtata](https://github.com/emehtata)

