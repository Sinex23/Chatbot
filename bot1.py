import google.generativeai as genai  # pip install google-generativeai
import pyttsx3  # pip install pyttsx3
import tkinter as tk  # pip install tk
from tkinter import scrolledtext, filedialog
import threading  # pip install thread
from PIL import Image, ImageTk, ImageDraw  # pip install pillow
import os

# Replace with your API key
GENAI_API_KEY = "AIzaSyB8xJnZ6WWBXkedW4AbrtwYB8EHTg6i0lg"

# Configure the Generative AI API with your key
genai.configure(api_key=GENAI_API_KEY)

# Load the appropriate model
model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure you're using the correct model name

# Initialize Text-to-Speech engine
engine = pyttsx3.init('sapi5')
engine.setProperty('voice', engine.getProperty('voices')[1].id)
engine.setProperty('rate', 180)  # Adjust speed
engine.setProperty('volume', 1.0)  # Set volume

is_paused = False

def speak(text):
    """Speak the given text smoothly without gaps."""
    global is_paused
    if is_paused:
        return
    engine.say(text)
    engine.runAndWait()

chat_history = []

def generate_response(query):
    """Generate a response for the given query using Google Gemini."""
    try:
        response = model.generate_content(query)
        return response.text if response.text else "Sorry, I couldn't generate a response."
    except Exception as e:
        return f"Sorry, I encountered an error: {e}"

def handle_conversation(query):
    """Respond to user input and store chat history."""
    response = generate_response(query)

    chat_history.append(f"You: {query}")
    chat_history.append(f"HariJ: {response}")

    display_user_message(query)
    display_bot_message(response)

    threading.Thread(target=speak, args=(response,)).start()

def display_user_message(message):
    """Display user's message in the chat window."""
    conversation_area.insert(tk.END, f"\n\nYou: {message}", "user")

def display_bot_message(message):
    """Display bot's response in the chat window."""
    conversation_area.insert(tk.END, f"\n\nHariJ: {message}", "bot")

def start_conversation(event=None):
    """Initialize conversation."""
    user_query = user_input.get()
    user_input.delete(0, tk.END)  # Clear the input field
    handle_conversation(user_query)

def end_conversation():
    """End conversation, save chat history, and close the application."""
    global stop_conversation
    stop_conversation = True

    with open("chat_history.txt", "w") as file:
        for chat in chat_history:
            file.write(chat + "\n")

    conversation_area.insert(tk.END, "\n\nHariJ: Conversation ended manually. Goodbye!", "bot")
    threading.Thread(target=speak, args=("Conversation ended manually. Goodbye!",)).start()
    root.quit()  # Close the application

def toggle_pause():
    """Pause or resume speaking."""
    global is_paused
    is_paused = not is_paused
    if is_paused:
        engine.stop()
        pause_button.config(text="Resume Speaking")
    else:
        pause_button.config(text="Pause Speaking")

def upload_file():
    """Allow users to upload a file and display it in the chat."""
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("All Files", "*.*"),
            ("Images", "*.png;*.jpg;*.jpeg;*.gif"),
            ("Documents", "*.pdf;*.docx;*.txt"),
            ("Videos", "*.mp4;*.avi;*.mov"),
        ]
    )

    if file_path:
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        # Display the file name in the chat window
        display_user_message(f"[Uploaded: {file_name}]")

        if file_extension in [".png", ".jpg", ".jpeg", ".gif"]:
            display_image(file_path)
        else:
            display_bot_message(f"File '{file_name}' uploaded successfully.")

def display_image(file_path):
    """Display uploaded images in the chat window."""
    try:
        img = Image.open(file_path)
        img.thumbnail((150, 150))  # Resize the image for display
        img = ImageTk.PhotoImage(img)

        image_label = tk.Label(conversation_area, image=img, bg="#2E2E3E")
        image_label.image = img
        conversation_area.window_create(tk.END, window=image_label)
        conversation_area.insert(tk.END, "\n")  # Newline for separation
    except Exception as e:
        display_bot_message(f"Error displaying image: {e}")

# Function to create a linear "+" symbol using Canvas
def create_linear_plus_icon():
    plus_canvas = tk.Canvas(user_input_frame, width=20, height=20, bg="#3E3E4E", bd=0, highlightthickness=0)
    
    # Draw a vertical line (centered)
    plus_canvas.create_line(10, 5, 10, 15, fill="white", width=2)
    
    # Draw a horizontal line (centered)
    plus_canvas.create_line(5, 10, 15, 10, fill="white", width=2)
    
    return plus_canvas

# Set up the GUI
root = tk.Tk()
root.title("HariJ - Chatbot")
root.geometry("600x650")
root.configure(bg="#1E1E2E")
root.resizable(True, True)

# Chat window
conversation_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=25, font=("Helvetica", 13), bg="#2E2E3E", fg="#E0E0E0", insertbackground="#FFFFFF", bd=0)
conversation_area.pack(padx=10, pady=10)

# Color tags
conversation_area.tag_configure("user", foreground="#FFCC00", font=("Helvetica", 14, "bold"))
conversation_area.tag_configure("bot", foreground="#66BB6A", font=("Helvetica", 13, "italic"))

# Input field
user_input_frame = tk.Frame(root, bg="#1E1E2E")
user_input_frame.pack(pady=10, fill="x", padx=10)

# Upload button with linear "+" symbol
upload_button = tk.Button(
    user_input_frame,
    text="+",  # Simple "+" symbol
    command=upload_file,
    font=("Helvetica", 18),  # Larger font size for visibility
    bg="#3E3E4E", fg="#FFFFFF",  # Matching background and foreground colors
    bd=0, padx=5, pady=0,  # Minimal padding for a clean look
    activebackground="#505050",  # Button color on hover
    activeforeground="#FFFFFF"   # Text color on hover
)
upload_button.pack(side="left", padx=5)

# Text input
user_input = tk.Entry(user_input_frame, font=("Helvetica", 14), width=35, bg="#3E3E4E", fg="#E0E0E0", bd=0, insertbackground="#FFFFFF")
user_input.pack(side="left", fill="x", expand=True, padx=5)

# Send button
send_button = tk.Button(user_input_frame, text="Send", font=("Helvetica", 12), command=start_conversation, bg="#5C6BC0", fg="#FFFFFF", bd=0, padx=15, pady=5)
send_button.pack(side="right", padx=5)

# Pause/Resume Button
pause_button = tk.Button(root, text="Pause Speaking", font=("Helvetica", 12), command=toggle_pause, bg="#FFA726", fg="#000000", bd=0, padx=15, pady=5)
pause_button.pack(pady=5)

# End button
end_button = tk.Button(root, text="End Conversation", font=("Helvetica", 12), command=end_conversation, bg="#F44336", fg="#FFFFFF", bd=0, padx=15, pady=5)
end_button.pack(pady=10)

# Bind Enter key
root.bind('<Return>', start_conversation)

root.mainloop()
