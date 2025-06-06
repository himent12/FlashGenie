FlashGenie
"Learn smarter, not harder."

FlashGenie is a smart flashcard generator and quiz app built with Python. It turns your plain text or CSV files into interactive flashcards, using spaced repetition techniques to help you retain knowledge more effectively over time.

✨ Features
📁 Import from CSV or Text
Easily load question/answer pairs from CSV files or formatted text.

🧠 Spaced Repetition
Uses a basic spaced repetition algorithm to prioritize cards you struggle with.

📝 Interactive Quizzing
CLI-based flashcard quiz mode with instant feedback.

📊 Progress Tracking
Stores your performance to adjust difficulty dynamically.

📦 Installation
bash
Copy
Edit
git clone https://github.com/yourusername/FlashGenie.git
cd FlashGenie
pip install -r requirements.txt
🚀 Usage
Prepare a CSV file like this:

csv
Copy
Edit
Question,Answer
What is the capital of France?,Paris
What does HTTP stand for?,HyperText Transfer Protocol
Run the app:

bash
Copy
Edit
python flashgenie.py
Follow the prompts to begin quizzing.

🛠️ Tech Stack
Python 3.x

pandas for data handling

(Optional) tkinter or rich for a better UI/UX in the future

📚 Future Features (Planned)
GUI with Tkinter or PyQt

Export results to CSV or JSON

Deck categories and filters

Online deck sharing support

🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

📄 License
MIT License

