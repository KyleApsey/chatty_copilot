# Chatty Co-Pilot

Chatty Co-Pilot is an interactive AI-powered co-pilot designed to enhance immersion and realism for virtual pilots in Microsoft Flight Simulator 2024 (or other simulators). The co-pilot engages in natural conversations, provides procedural assistance, and responds with personality-driven voices, adding a new dimension to your flight experience.

## Current Features
- **Conversational AI**: The co-pilot responds conversationally using OpenAI's GPT API.
- **Personality Customization**: Select from multiple personalities (Friendly, Professional, Sarcastic, Nervous, and Annoyed) to match your preferred flight atmosphere.
- **Text-to-Speech Integration**: Azure Cognitive Services provides dynamic voices tailored to the chosen personality.
- **Conversation Context**: The AI remembers conversation history for continuity, utilizing a summarization strategy to manage memory efficiently.
- **Real-Time Interaction**: Uses a hotkey system to start and stop speech recognition for hands-free interaction.
- **Modular Design**: Designed with flexibility and scalability for future features and improvements.

## Roadmap

### **Phase 1: Initial AI Integration - _Ears and Mouth_ (Completed)**
- [x] Basic conversational capabilities.
- [x] Speech recognition via Google Speech Recognition API.
- [x] Text-to-Speech integration with Azure Cognitive Services.
- [x] Personality-based interaction and voices.
- [x] Summarization for efficient memory management in conversations.

### **Phase 2: Enhanced Interactivity - _Eyes Phase 1_ (In Progress)**
- [ ] Implement dynamic checklists for various flight phases (e.g., Startup, Taxi, Takeoff, Landing, Shutdown).
- [ ] Introduce SimConnect integration to provide awareness of:
  - [ ] Pre-flight briefings (passenger/weight details, procedure deviations).
  - [ ] Weather feedback during taxi (wind, icing risks, etc.).
  - [ ] Mid-flight alerts for warnings or cautions.
  - [ ] Post-flight recap (flight time, speed, altitude, etc.).
- [ ] Expand the list of personalities and refine existing ones for greater diversity and immersion.

### **Phase 3: Advanced Simulator Integration - _Eyes Phase 2_**
- [ ] Deepen SimConnect integration for real-time co-pilot awareness:
  - [ ] React to extreme vertical speeds or abrupt altitude changes.
  - [ ] Report distance to and altitude of the next waypoint as it’s passed.
  - [ ] Warn about fuel levels (single warning to avoid repetition).
  - [ ] Announce and respond to warnings or cautions when taxiing or in-flight.
- [ ] Trigger co-pilot responses and actions based on simulator events.
- [ ] Allow the co-pilot to manage controls (e.g., set autopilot parameters, flaps, landing gear) upon request.

### **Phase 4: Application Packaging**
- [ ] Create a user-friendly GUI for configuration and operation.
- [ ] Package the project as a standalone application.
- [ ] Provide settings for custom checklists and additional configurations.

### **Phase 5: Immersive Add-Ons**
- [ ] Support custom AI training for user-specific co-pilot styles.
- [ ] Introduce advanced co-pilot features (e.g., flight planning, ATC interaction).
- [ ] Enable real-time companion apps (phone/tablet) for gauges, warnings, and data visualization.

## Requirements
- **Python 3.8+**
- **Packages**:
  - `pynput`
  - `speech_recognition`
  - `azure-cognitiveservices-speech`
  - `openai`
  - `python-dotenv`
- **APIs**:
  - OpenAI API Key
  - Azure Cognitive Services Speech Key and Region

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/KyleApsey/chatty_copilot.git
   cd chatty_copilot
   ```
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
   ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
   ```
4. Set up your .env file with your API keys:
    ```makefile
    OPENAI_API_KEY=your_openai_key
    AZURE_SPEECH_KEY=your_azure_speech_key
    AZURE_SERVICE_REGION=your_azure_region
   ```
## Usage
Run the application from the command line:
  ```bash
  python main.py
  ```
Press:
- `Space` to toggle listening
- `Esc` to exit the program
Follow prompts to select a co-pilot personality and start interacting!

## Contributing
Contributions are welcome! Feel free to fork this repository, submit pull requests, or suggest ideas through issues.

## License
This project is licensed under the MIT License.
