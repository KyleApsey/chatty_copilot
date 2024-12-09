# Handles all chat-related logic (e.g., Speech recognition, integrating OpenAI API, creating the AI response).
import os
import threading
from pynput.keyboard import Key, Listener
import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

# Check if the API key is set
if not os.getenv("OPENAI_API_KEY"):
  raise ValueError("API key is missing. Please set it in your .env file.")

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Azure Speech configuration
azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
azure_service_region = os.getenv("AZURE_SERVICE_REGION")
speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key, region=azure_service_region)
speech_config.speech_synthesis_voice_name = "en-US-Andrew2:DragonHDLatestNeural" # https://speech.microsoft.com/portal/voicegallery


# Local scoped flags
is_listening = False
stop_listening = threading.Event()  # Event to signal when to stop listening
speech_fragments = []  # List to store speech fragments
conversation_history = []  # List to store conversation history
history_threshold = 20  # Maximum number of messages to retain in the history
chosen_personality = None
personalities = {
  "professional": {
    "role": "system",
    "content": "You are a highly experienced co-pilot with an analytical and professional demeanor.  You're polite, but you keep your answers short, technical and to the point."
  },
  "friendly": {
    "role": "system",
    "content": "You are a friendly and enthusiastic co-pilot with a passion for aviation.  You enjoy talking with the pilot and often make small talk, but of course within reason."
  },
  "sarcastic": {
    "role": "system",
    "content": "You are a sarcastic and witty co-pilot who loves cracking jokes.  You get really annoyed when people don't understand you, your jokes, or things you determine are common sense."
  },
  "annoyed": {
    "role": "system",
    "content": "You are a sarcastic and annoyed co-pilot who is ready to be done for the day.  You get really annoyed when people don't understand you or things you determine are common sense.  You're not in the mood for jokes or games."
  },
  "nervous": {
    "role": "system",
    "content": "You are a anxious and nervous passenger sitting in the co-pilot's seat.  You were put up to this flight by your friend, the pilot, and you want to help out but you're slightly uncomfortable and scared."
  }
}

def select_personality():
  """Prompt the user to select a personality."""
  global chosen_personality
  while chosen_personality not in personalities:
    print("Available personalities: professional, friendly, sarcastic, or nervous.")
    chosen_personality = input("Please select a personality type and press 'Enter' to continue: ").strip().lower()
    if chosen_personality not in personalities:
      print(f"'{chosen_personality}' is not a valid option. Please try again.")
  print(f"Personality selected: {chosen_personality.capitalize()}")

def listen_to_user():
  """Continuously listen to the user's voice input until stopped."""
  global speech_fragments
  recognizer = sr.Recognizer()
  with sr.Microphone() as source:
    print("Listening... Press 'space' again to stop.")
    recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for background noise
    while not stop_listening.is_set():
      try:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Listen for up to 10 seconds
        text = recognizer.recognize_google(audio)
        speech_fragments.append(text)  # Append recognized text to the list
        print(f"You said: {text}")
      except sr.WaitTimeoutError:
        print("I didn't hear anything. Please try again.")
      except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said. Please try again.")
      except sr.RequestError as error:
        print(f"listen_to_user() - An error occurred: {error}")
      except Exception as e:
        print(f"Unexpected error: {e}")

def handle_chat(user_input):
  """Respond to user input using OpenAI's GPT-4o model."""
  global conversation_history

  try:
    # Ensure the personality prompt is integrated into the system message
    personality_message = personalities[chosen_personality]["content"]
    system_message = f"{personality_message} " \
                     f"You will be speaking with the flight captain who may ask you questions about flying the plane as well as general discussion. " \
                     f"You should be chatty in your responses, but they must be no longer than 3 sentences. " \
                     f"Please make sure that you answer technically, as you are a copilot after all, and depending on our mission, between 2 and 300 souls are counting on accurate information."

    # Add system message at the start if not already present
    if not conversation_history or conversation_history[0]["role"] != "system":
      conversation_history.insert(0, {"role": "system", "content": system_message})

    # Append the user's input
    conversation_history.append({"role": "user", "content": user_input})

    # Prune and summarize if necessary
    prune_and_summarize_history()

    # Send only the recent messages (e.g., last 20 messages)
    conversation_to_send = conversation_history[-history_threshold:]

    # Call OpenAI API
    response = client.chat.completions.create(
      messages=conversation_to_send,
      model="gpt-4o-mini",
    )

    # Extract and save the response
    ai_response = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": ai_response})

    return ai_response
  except Exception as error:
    return f"handle_chat() - An error occurred: {error}"


def handle_text_to_speech(text):
  """Convert text to speech using Azure Speech Services with personality-based voices."""
  try:
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Map personality to specific voice
    personality_voices = {
      "friendly": "en-US-Andrew2:DragonHDLatestNeural",
      "professional": "en-US-SerenaMultilingualNeural",
      "sarcastic": "en-US-SteffanMultilingualNeural",
      "annoyed": "en-US-SaraNeural",
      "nervous": "en-US-GuyNeural"
    }

    # Set the voice dynamically based on the chosen personality
    if chosen_personality in personality_voices:
      synthesizer.voice_name = personality_voices[chosen_personality]
    else:
      synthesizer.voice_name = "en-US-Andrew2:DragonHDLatestNeural"  # Default voice

    # Synthesize speech
    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
      print("Response spoken successfully.")
    else:
      print(f"Failed to synthesize response: {result.reason}")
      return text
  except Exception as error:
    print(f"handle_text_to_speech() - An error occurred: {error}")
    return "I'm sorry, something went wrong."



def start_listening():
  """Start the continuous voice recognition."""
  global is_listening, speech_fragments
  if not is_listening:
    is_listening = True
    speech_fragments = []  # Reset the fragments
    stop_listening.clear()  # Reset the stop signal
    print("Waiting for input...")
    threading.Thread(target=listen_to_user).start()


def stop_listening_handler():
  """Stop the continuous voice recognition."""
  global is_listening, speech_fragments
  if is_listening:
    stop_listening.set()  # Signal to stop listening
    is_listening = False
    # Combine all fragments into a single string
    full_text = " ".join(speech_fragments)
    print(f"Full combined text: {full_text}")
    # Get the response from the AI model
    response = handle_chat(full_text)
    print(f"Chatty Copilot: {response}") # Print the response, so that we can see it in the console for debugging
    # Convert the response to speech
    handle_text_to_speech(response)
    print("Stopped listening. Press 'space' to start again or 'esc' to exit.")


def on_press(key):
  """Handle key press events."""
  global chosen_personality
  if key == Key.space:  # Toggle listening on space press
    if is_listening:
      stop_listening_handler()
    else:
      if chosen_personality is None:
        select_personality()
      start_listening()

def on_release(key):
  """Handle key release events."""
  if key == Key.esc:  # Stop the listener on escape key
    print("Exiting...")
    return False  # Stops the Listener

def start_chat_listener():
  """Start the keyboard listener for chat functionality."""
  print("Ready. Press 'space' to toggle listening or 'esc' to exit.")
  with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

def summarize_conversation(messages):
  """Summarize old conversation messages."""
  summary_prompt = "Summarize the following conversation concisely:\n"
  for message in messages:
    summary_prompt += f"{message['role'].capitalize()}: {message['content']}\n"

  try:
    response = client.chat.completions.create(
      messages=[{"role": "system", "content": summary_prompt}],
      model="gpt-4o-mini",
    )
    return response.choices[0].message.content  # Return the summarized text
  except Exception as e:
    print(f"Error during summarization: {e}")
    return None

def prune_and_summarize_history():
  """Summarize older messages to retain context."""
  global conversation_history

  # Only prune if the history exceeds the threshold
  if len(conversation_history) > history_threshold:
    # Extract the first N messages for summarization, excluding the system message
    old_messages = conversation_history[1:1 + (history_threshold // 2)]  # Use half the threshold for summarization
    summary = summarize_conversation(old_messages)

    if summary:
      # Replace the old messages with the summary
      conversation_history = (
        [conversation_history[0]]  # Keep the system message
        + [{"role": "system", "content": f"Summary: {summary}"}]  # Add the summary
        + conversation_history[1 + (history_threshold // 2):]  # Keep the rest of the history
      )
      print(f"Summarized old messages: {summary}")
    else:
      print("Failed to summarize old messages.")


