# 🧞‍♂️ FlashGenie

> _"Learn smarter, not harder."_

FlashGenie is a powerful and beginner-friendly flashcard app built with Python. Whether you're prepping for exams, learning a new language, or just trying to retain more information, FlashGenie takes your raw data (CSV or text) and turns it into interactive flashcards—optimized by **spaced repetition** for long-term memory.

---

## 📸 Preview

![FlashGenie Screenshot](https://user-images.githubusercontent.com/yourusername/flashgenie-preview.png)  
> _Simple terminal interface (GUI coming soon!)_

---

## 🎯 Key Features

- ✅ **Import Flashcards Instantly**
  - Accepts `.csv` and formatted `.txt` files
  - Supports custom delimiters and flexible question/answer layouts

- 🧠 **Spaced Repetition Algorithm**
  - Boosts long-term retention by repeating difficult cards more often
  - Tracks your performance over time

- 🖥️ **Terminal-Based Quiz Mode**
  - Clean CLI interface
  - Instant feedback and score tracking

- 📊 **Performance Tracking**
  - Optional CSV logging of your quiz sessions
  - See your improvement over time

- 🔒 **Offline, Private & Secure**
  - No ads, no trackers—100% offline and personal

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/FlashGenie.git
cd FlashGenie
2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
```
✅ FlashGenie uses only a few dependencies and is easy to install.

3. Prepare a Flashcard File
You can use either .csv or .txt format.
CSV Format Example: csv, Copy, Edit, Question and Answer.
What is the capital of France?
Paris
What does CPU stand for?
Central Processing Unit


TXT Format Example: text, Copy, and Edit.

Q: What is the capital of Japan?
A: Tokyo

Q: What gas do plants absorb?
A: Carbon Dioxide

🧪 Usage: bash, Copy, and Edit.
python flashgenie.py
Choose your flashcard file

Begin answering questions

Get live feedback on correct and incorrect answers

Let the spaced repetition system handle what comes next

🛠️ Tech Stack
Language	Libraries Used	Function
Python	pandas	CSV handling
datetime, json	Logging & time tracking
colorama (opt.)	Terminal coloring (enhanced UX)

📈 Roadmap
 CSV and text file support

 Spaced repetition quiz logic

 GUI with Tkinter

 Deck tagging (e.g., "Biology", "French", "SAT")

 Import from Quizlet/Anki

 Export stats dashboard (charts with Matplotlib)

 Web version using Flask or Django

🧑‍💻 Contributing
Pull requests are welcome! Whether you want to:

Add new features

Fix bugs

Suggest better algorithms or UX

Help with GUI development

Please open an issue or submit a PR with a clear explanation.

📄 License
This project is licensed under the MIT License.
See LICENSE file for details.

🌟 Support & Feedback
If you like this project, please consider ⭐ starring the repo!

Have feedback or suggestions?
Open an issue or contact me at Huckflower@gmail.com.

🙌 Acknowledgments
Inspired by Anki's spaced repetition concept

Thanks to the open-source Python community

Built with 💻, ☕, and a lot of trial & error!

