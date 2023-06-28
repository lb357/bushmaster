import re
import tkinter as tk
import json
from tkinter import filedialog as fd
import sys
import subprocess
from bushmaster import help_screen, docs_screen, translate, retranslate

version = "1.0"
current_file = None


quotation_marks = ["'", '"']
structural_separators = ["[", "]", "{", "}", "(", ")"]
operators = ["=", ">", "<", "*", "&", "|", "/", "+", "-", "%", "!", "^", "~", ":"]
with open("keywords.json", encoding='utf-8') as file:
    translation_dictionary = json.loads(file.read())


class CustomText(tk.Text):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        # sample tag

    def highlight(self, tag, start, end):
        self.tag_add(tag, start, end)

    def highlight_all(self, pattern, tag):
        for match in self.search_re(pattern):
            self.highlight(tag, match[0], match[1])

    def clean_highlights(self, tag):
        self.tag_remove(tag, "1.0", tk.END)

    def search_re(self, pattern):
        matches = []
        text = self.get("1.0", tk.END).splitlines()
        for i, line in enumerate(text):
            for match in re.finditer(pattern, line):
                matches.append((f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}"))

        return matches

    def highlight_pattern(self, pattern, tag="keyword"):
        self.clean_highlights(tag)
        self.highlight_all(pattern, tag)

    def highlight_text(self, args):
        self.tag_config(f"int", foreground="DarkOrange4")
        self.highlight_pattern(rf'\d', f"int")
        self.tag_config(f"float", foreground="DarkOrange2")
        self.highlight_pattern(rf'\d\.\d', f"float")
        for i in operators:
            self.tag_config(f"operators{i}", foreground="Blue")
            self.highlight_pattern(rf'\{i}', f"operators{i}")
        for i, k in translation_dictionary.items():
            self.tag_config(rf"keyword{i}", foreground="MediumPurple4")
            self.highlight_pattern(rf"\b{i}\b", rf"keyword{i}")
            self.tag_config(rf"keyword{k}", foreground="MediumPurple2")
            self.highlight_pattern(rf"\b{k}\b", rf"keyword{k}")
        for i in structural_separators:
            self.tag_config(f"structural_separators{i}", foreground="Gray")
            self.highlight_pattern(rf'\{i}', f"structural_separators{i}")
        for i in quotation_marks:
            self.tag_config(f"quotation_marks{i}", foreground="PaleGreen4")
            self.highlight_pattern(rf'\{i}(.*?)\{i}', f"quotation_marks{i}")
        self.tag_config(f"quotation_marks_multistring", foreground="PaleGreen2")
        self.highlight_pattern(rf'"""', f"quotation_marks_multistring")
        self.tag_config(f"comment", foreground="Red")
        self.highlight_pattern(rf'#(.*)', f"comment")


def start():
    global current_file
    save()

    print(f"\nСТАРТ {current_file}")
    if current_file is None:
        subprocess.run(["cmd.exe", "/c", "start", "bushmaster.py"])

    else:
        subprocess.run(["cmd.exe", "/c", "start", "bushmaster.py", current_file, "-IDE"])

def new():
    text.delete(1.0, tk.END)
    current_file = None
    root.title(f"IDE bushmaster | {current_file}")
    print("\nНОВЫЙ ФАЙЛ")

def save():
    try:
        global current_file
        file_name = fd.asksaveasfilename(defaultextension=".*",
            filetypes=(("Файл скрипта Бушмейстер", ".bm"),
                       ("Файл скрипта Python", ".py")))
        f = open(file_name, 'w', encoding='utf-8')
        s = text.get(1.0, tk.END)
        f.write(s)
        f.close()
        current_file = file_name
        root.title(f"IDE bushmaster | {current_file}")
        print(f"\nСОХРАНЁН ФАЙЛ {current_file}")
    except Exception as error:
        print(f"\nОШИБКА СОХРАНЕНИЯ ФАЙЛА: {error}")

def open_():
    try:
        global current_file
        file_name = fd.askopenfilename()
        f = open(file_name, encoding='utf-8')
        s = f.read()
        text.delete(1.0, tk.END)
        text.insert(1.0, s)
        text.highlight_text(None)
        f.close()
        current_file = file_name
        root.title(f"IDE bushmaster | {current_file}")
    except Exception as error:
        print(f"\nОШИБКА ОТКРЫТИЯ ФАЙЛА: {error}")

def exit_():
    sys.exit()

def help_():
    print(help_screen)

def docs():
    print(docs_screen)

def translate_():
    txt = translate(text.get(1.0, tk.END))
    text.delete(1.0, tk.END)
    text.insert(1.0, txt)
    text.highlight_text(None)

def retranslate_():
    txt = retranslate(text.get(1.0, tk.END))
    text.delete(1.0, tk.END)
    text.insert(1.0, txt)
    text.highlight_text(None)


if __name__ == "__main__":
    root = tk.Tk()
    root.title(f"IDE bushmaster | {current_file}")

    mainmenu = tk.Menu(root)
    root.config(menu=mainmenu)
    text = CustomText(root)

    text.pack(expand=True, fill='both')
    text.bind("<KeyRelease>", text.highlight_text)

    filemenu = tk.Menu(mainmenu, tearoff=0)
    filemenu.add_command(label="Запуск", command=start)
    filemenu.add_command(label="Новый", command=new)
    filemenu.add_command(label="Сохранить", command=save)
    filemenu.add_command(label="Открыть", command=open_)
    filemenu.add_command(label="Выход", command=exit_)

    translatemenu = tk.Menu(mainmenu, tearoff=0)
    translatemenu.add_command(label="Транслировать (bm -> py)", command=translate_)
    translatemenu.add_command(label="Ретранслировать (py -> bm)", command=retranslate_)

    helpmenu = tk.Menu(mainmenu, tearoff=0)
    helpmenu.add_command(label="Справка", command=help_)
    helpmenu.add_command(label="Документация", command=docs)

    mainmenu.add_cascade(label="Файл", menu=filemenu)
    mainmenu.add_cascade(label="Транслирование", menu=translatemenu)
    mainmenu.add_cascade(label="Помощь", menu=helpmenu)
    root.mainloop()

