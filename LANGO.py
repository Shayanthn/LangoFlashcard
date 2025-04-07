# فلش‌کارت ایتالیایی شایان با بررسی نوشتاری دقیق (بدون تشخیص گفتار)

import tkinter as tk
from tkinter import messagebox
import json
import os
import random
from gtts import gTTS
from playsound import playsound

DATA_FILE = 'words.json'
PRONUNCIATION_FOLDER = 'pronunciations'

if not os.path.exists(PRONUNCIATION_FOLDER):
    os.makedirs(PRONUNCIATION_FOLDER)

# بارگذاری و ذخیره‌سازی

def load_words():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_words(words):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

# گرفتن تلفظ آنلاین و ذخیره‌سازی

def download_pronunciation(word):
    try:
        tts = gTTS(word, lang='it')
        filepath = os.path.join(PRONUNCIATION_FOLDER, f"{word}.mp3")
        tts.save(filepath)
    except Exception as e:
        messagebox.showerror("خطا در تلفظ", f"تلفظ دانلود نشد: {e}")

# افزودن لغت

def add_word():
    italian = entry_italian.get().strip().lower()
    persian = entry_persian.get().strip()

    if not italian or not persian:
        messagebox.showerror("خطا", "هر دو فیلد باید پر شوند.")
        return

    words = load_words()
    if italian in words:
        messagebox.showinfo("موجود", "این لغت قبلاً وارد شده.")
        return

    words[italian] = {"meaning": persian, "status": "practice"}
    save_words(words)
    download_pronunciation(italian)

    messagebox.showinfo("ذخیره شد", f"لغت '{italian}' ذخیره و تلفظش دریافت شد.")
    entry_italian.delete(0, tk.END)
    entry_persian.delete(0, tk.END)
    update_stats()

# آزمون

quiz_list = []
current_index = 0
current_audio_path = ""
daily_required = 50
daily_correct = 0

def start_quiz():
    global quiz_list, current_index, daily_correct
    words = load_words()
    all_count = len(words)
    quiz_list = [w for w in words if words[w]['status'] == 'practice']

    if not quiz_list:
        messagebox.showinfo("آزمون", "لغتی برای تمرین وجود ندارد.")
        return

    if all_count >= 100 and len(quiz_list) < daily_required:
        messagebox.showwarning("تسک روزانه ناقص", f"حداقل باید ۵۰ لغت تمرین کنی. الان فقط {len(quiz_list)} لغت آماده تمرینه.")
        return

    random.shuffle(quiz_list)
    current_index = 0
    daily_correct = 0
    show_next_question()

def show_next_question():
    global current_audio_path
    if current_index >= len(quiz_list):
        messagebox.showinfo("پایان آزمون", "برای مشاهده عملکرد روزانه دکمه 'پایان آزمون' را بزنید.")
        lbl_question.config(text="آزمونی وجود ندارد")
        update_stats()
        return

    word = quiz_list[current_index]
    meaning = load_words()[word]["meaning"]
    lbl_question.config(text=f"معنی: {meaning}")
    entry_answer.delete(0, tk.END)
    current_audio_path = os.path.join(PRONUNCIATION_FOLDER, f"{word}.mp3")

    try:
        if os.path.exists(current_audio_path):
            playsound(current_audio_path)
        else:
            tts = gTTS(word, lang='it')
            tts.save(current_audio_path)
            playsound(current_audio_path)
    except:
        pass

def check_answer():
    global current_index, daily_correct
    user_answer = entry_answer.get().strip().lower()
    correct_word = quiz_list[current_index]

    if user_answer != correct_word.lower():
        messagebox.showwarning("اشتباه", f"جواب اشتباهه. جواب درست: {correct_word}")
    else:
        messagebox.showinfo("درست!", "✅ آفرین، درست جواب دادی!")
        words = load_words()
        words[correct_word]["status"] = "known"
        save_words(words)
        daily_correct += 1

    current_index += 1
    show_next_question()

def play_pronunciation():
    word = quiz_list[current_index] if current_index < len(quiz_list) else None
    if not word:
        messagebox.showinfo("پایان", "لغتی برای تلفظ وجود ندارد.")
        return
    filepath = os.path.join(PRONUNCIATION_FOLDER, f"{word}.mp3")
    try:
        if os.path.exists(filepath):
            playsound(filepath)
        else:
            tts = gTTS(word, lang='it')
            tts.save(filepath)
            playsound(filepath)
    except Exception as e:
        messagebox.showerror("خطا", f"پخش تلفظ ممکن نشد: {e}")

def end_quiz():
    total = len(quiz_list)
    incorrect = total - daily_correct

    if len(load_words()) >= 100 and total < daily_required:
        messagebox.showwarning("تسک ناقص", f"برای پایان آزمون باید حداقل {daily_required} لغت تمرین کنی.")
        return

    msg = f"""📊 عملکرد امروز:
🔹 کل لغات تمرین شده: {total}
✅ درست پاسخ داده شده: {daily_correct}
❌ نادرست: {incorrect}"""

    if total >= daily_required:
        if daily_correct >= daily_required:
            msg += "\n🎯 تسک روزانه با موفقیت انجام شد!"
        else:
            msg += "\n⚠️ تسک روزانه انجام نشد."

    messagebox.showinfo("گزارش روزانه", msg)


def reset_known_words():
    words = load_words()
    count = 0
    for w in words:
        if words[w]["status"] == "known":
            words[w]["status"] = "practice"
            count += 1
    save_words(words)
    messagebox.showinfo("بازنشانی", f"{count} لغت از بلدها به تمرینی منتقل شد.")
    update_stats()

def update_stats():
    words = load_words()
    total = len(words)
    known = len([w for w in words if words[w]["status"] == "known"])
    practice = len([w for w in words if words[w]["status"] == "practice"])
    lbl_stats.config(text=f"📊 کل: {total} | بلد: {known} | تمرینی: {practice}")

# رابط گرافیکی

root = tk.Tk()
root.title("فلش کارت ایتالیایی شایان")

try:
    farsi_font = ("B Nazanin", 12)
except:
    farsi_font = ("Tahoma", 12)
english_font = ("Arial", 10)

# افزودن لغت

tk.Label(root, text="لغت ایتالیایی:", font=farsi_font).grid(row=0, column=0, padx=10, pady=5)
entry_italian = tk.Entry(root, width=30, font=english_font)
entry_italian.grid(row=0, column=1)

tk.Label(root, text="معنی فارسی:", font=farsi_font).grid(row=1, column=0, padx=10, pady=5)
entry_persian = tk.Entry(root, width=30, font=farsi_font)
entry_persian.grid(row=1, column=1)

btn_save = tk.Button(root, text="ذخیره و تلفظ", font=farsi_font, command=add_word)
btn_save.grid(row=2, column=0, columnspan=2, pady=10)

# آزمون

tk.Label(root, text="-------------------------------", font=english_font).grid(row=3, column=0, columnspan=2)

btn_start_quiz = tk.Button(root, text="شروع آزمون", font=farsi_font, command=start_quiz)
btn_start_quiz.grid(row=4, column=0, columnspan=2, pady=5)

lbl_question = tk.Label(root, text="آزمونی وجود ندارد", font=farsi_font)
lbl_question.grid(row=5, column=0, columnspan=2, pady=5)

entry_answer = tk.Entry(root, width=30, font=english_font)
entry_answer.grid(row=6, column=0, columnspan=2)

btn_submit = tk.Button(root, text="ثبت پاسخ", font=farsi_font, command=check_answer)
btn_submit.grid(row=7, column=0, columnspan=2, pady=10)

btn_pronounce = tk.Button(root, text="🔊 پخش تلفظ", font=farsi_font, command=play_pronunciation)
btn_pronounce.grid(row=8, column=0, columnspan=2, pady=5)

btn_end = tk.Button(root, text="پایان آزمون و گزارش عملکرد", font=farsi_font, command=end_quiz)
btn_end.grid(row=9, column=0, columnspan=2, pady=5)

lbl_stats = tk.Label(root, text="📊 آمار در حال بارگذاری...", font=farsi_font)
lbl_stats.grid(row=10, column=0, columnspan=2, pady=5)

btn_reset = tk.Button(root, text="🔁 بازگردانی لغات بلد به تمرینی", font=farsi_font, command=reset_known_words)
btn_reset.grid(row=11, column=0, columnspan=2, pady=10)

lbl_footer = tk.Label(
    root,
    text="ساخته شده توسط شایان طاهرخانی\nGitHub: shayanthn | Email: shayanthn78@gmail.com",
    font=("Arial", 8),
    fg="gray"
)
lbl_footer.grid(row=12, column=0, columnspan=2, pady=15)

update_stats()
root.mainloop()
"""CREATED BY : SHAYAN TAHERKHANI 
EMAIL : SHAYANTHN78@GMAIL.COM
LINKEDIN : LINKEDIN.COM/IN/SHAYANTAHERKHANI
GITHUB : SHAYANTHN
"""
