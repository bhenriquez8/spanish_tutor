import tkinter as tk
from tkinter import ttk
from engine import normalize_sentence, compare_translation
from deepl_client import translate_with_deepl

class SpanishTrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spanish Past Tense Trainer")
        self.root.geometry("600x400")

        self.build_ui()
        self.sentence_label.config(text=self.get_next_sentence())

    def build_ui(self):
        main = ttk.Frame(self.root, padding=20)
        main.pack(fill="both", expand=True)

        # Instruction
        self.instruction = ttk.Label(
            main,
            text="Translate the sentence into Spanish:",
            font=("Arial", 12)
        )
        self.instruction.pack(anchor="w", pady=(0, 10))

        # Sentence prompt
        self.sentence_label = ttk.Label(
            main,
            text="I was walking to the store.",
            font=("Arial", 14, "bold"),
            wraplength=540
        )
        self.sentence_label.pack(pady=(0, 20))

        # User input
        self.entry = ttk.Entry(main, font=("Arial", 12))
        self.entry.pack(fill="x", pady=(0, 10))
        self.entry.focus()

        # Submit button
        self.submit_btn = ttk.Button(
            main,
            text="Submit",
            command=self.on_submit
        )
        self.submit_btn.pack(pady=(0, 20))

        # Next sentence button
        self.next_btn = ttk.Button(
            main,
            text="Next sentence",
            command=self.on_next_sentence
        )
        self.next_btn.pack(pady=(0, 20))

        # Feedback box
        self.feedback = tk.Text(
            main,
            height=4,
            wrap="word",
            font=("Arial", 11),
            state="disabled"
        )
        self.feedback.pack(fill="x")

        # Deepl reference label
        self.deepl_label = ttk.Label(
            main,
            text="Reference translation (DeepL):",
            font=("Arial", 10, "italic")
        )
        self.deepl_label.pack(anchor="w", pady=(10, 0))

        # DeepL reference text
        self.deepl_text = tk.Text(
            main,
            height=3,
            wrap="word",
            font=("Arial", 11),
            state="disabled",
            foreground="gray",
        )
        self.deepl_text.pack(fill="x", pady=(0,5))

    def on_submit(self):
        user_input = self.entry.get().strip()

        # Temporary placeholder feedback
        if not user_input:
            self.show_feedback("Please enter a translation.", "red")
        else:
            self.show_feedback("Processing your answer...", "blue")

        self.disable_submit()

        try:
            eng_sentence = self.sentence_label["text"]

            # 1. Get DeepL translation
            deepl_translation = translate_with_deepl(eng_sentence)
            self.show_deepl_translation(deepl_translation)

            # 2. Normalize both
            user_words = normalize_sentence(user_input)
            deepl_words = normalize_sentence(deepl_translation)

            # 3. Compare (tense detection can be subbed for now)
            result = compare_translation(
                user_words,
                deepl_words,
                user_tense=None, # temporary
                deepl_tense=None # temporary
            )

            # 4. Map result to feedback
            feedback_text, color = self.map_result_to_feedback(result)
            self.show_feedback(feedback_text, color)

        except Exception as e:
            self.show_feedback(f"Error: {e}", "red")

        finally:
            self.enable_submit()

    def reset_ui_state(self):
        # Clear entry
        self.entry.delete(0, "end")

        # Clear feedback
        self.feedback.config(state="normal")
        self.feedback.delete("1.0", "end")
        self.feedback.config(state="disabled")

        # Clear DeepL reference
        self.deepl_text.config(state="normal")
        self.deepl_text.delete("1.0", "end")
        self.deepl_text.config(state="disabled")

        # Re-enable submit
        self.enable_submit()

        # Focus input
        self.entry.focus()

    # HELPER FUNCTIONS
    def map_result_to_feedback(self, result):
        if result == "perfect":
            return "Perfect! Your translation matches exactly.", "green"

        if result == "correct_different_phrasing":
            return "Correct! Your phrasing is different but accurate.", "orange"

        if result == "incorrect_tense":
            return "The meaning is close, but the tense is incorrect.", "orange"

        if result == "incorrect":
            return "Not quite. Review the verb tense again.", "red"

        return "Unexpected result.", "red"

    def show_feedback(self, message, color):
        self.feedback.config(state="normal")
        self.feedback.delete("1.0", "end")
        self.feedback.insert("end", message)
        self.feedback.tag_add("color", "1.0", "end")
        self.feedback.tag_config("color", foreground=color)
        self.feedback.config(state="disabled")

    def get_next_sentence(self):
        # TEMPORARY - replace later with real sentence selection
        sentences = [
            "I was walking to the store",
            "We ate dinner together",
            "She was reading when I arrived.",
            "They played soccer yesterday"
        ]

        if not hasattr(self, "_sentence_index"):
            self._sentence_index = 0
        else:
            self._sentence_index = (self._sentence_index + 1) % len(sentences)

        return sentences[self._sentence_index]

    def on_next_sentence(self):
        new_sentence = self.get_next_sentence()
        self.sentence_label.config(text=new_sentence)
        self.reset_ui_state()

    def show_deepl_translation(self, text):
        self.deepl_text.config(state="normal")
        self.deepl_text.delete("1.0", "end")
        self.deepl_text.insert("end", text)
        self.deepl_text.config(state="disabled")

    def disable_submit(self):
        self.submit_btn.config(state="disabled")
        self.submit_btn.config(text="Checking...")

    def enable_submit(self):
        self.submit_btn.config(state="normal")
        self.submit_btn.config(text="Submit")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpanishTrainerGUI(root)
    root.mainloop()

