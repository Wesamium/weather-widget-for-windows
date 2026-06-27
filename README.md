# WeatherWidget 🌦️

A sleek, minimalist desktop weather widget that provides real-time updates directly on your desktop or in your system tray.

## Features

- **Real-time Updates**: Automatically fetches and displays temperature, conditions, and icons from OpenWeatherMap.
- **System Tray Integration**: Minimize the widget to your system tray for a clutter-free workspace.
- **Custom Locations**: Easily change your current city via an integrated settings drawer.
- **Modern UI**: A clean, dark-themed interface designed for seamless integration into any desktop environment.
- **Interactive Elements**: Support for dragging the window and a context menu for quick actions.

## Getting Started

### Prerequisites

- Python 3.x
- An [OpenWeatherMap API Key](https://openweathermap.org/api)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Wesamium/WeatherWidget.git
   cd WeatherWidget
   ```

2. **Install dependencies:**
   ```bash
   pip install requests pystray Pillow python-dotenv
   ```

3. **Configuration:**
   Create a `.env` file in the root directory and add your API key:
   ```env
   OPENWEATHER_API_KEY=your_api_key_here
   ```

4. **Run the application:**
   ```bash
   python main.pyw
   ```

## Usage

- **Run automatically on Windows start**: Win + R, type in shell:startup to open the C:\Users\username\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup Folder. 
Then put a shortcut of the main.pyw in that folder.
- **Settings**: Click the ⚙ icon to open the settings drawer and enter a new city name.
- **Minimize**: Click the ✕ button to hide the widget into the system tray.
- **Tray Menu**: Right-click the widget or the tray icon to access the Exit Completely option.

## Support & Resources

- **Documentation**: For detailed information on API usage, visit the [OpenWeatherMap Documentation](https://openweathermap.org/api).

## Contributing

Contributions are welcome! 
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

This project is licensed under the terms specified in the `LICENSE` file.

## Acknowledgement
Developed with the help of Gemini as AI collaborator, who helped refine the frameless UI layout, dynamic icon streaming integration, and pystray multi-threaded system tray architecture.
