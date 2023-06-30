import re
import tkinter as tk
import json
from tkinter import filedialog as fd
import sys
import subprocess
import os
from bushmaster import help_screen, docs_screen, translate, retranslate
from tkinter.messagebox import showinfo
import tkinter.font as tkfont

version = "1.0"
current_file = None
build_extension = "py" #The extension of the main Bushmeister file (such as py, exe and others)

quotation_marks = ["'", '"']
structural_separators = ["[", "]", "{", "}", "(", ")"]
operators = ["=", ">", "<", "*", "&", "|", "/", "+", "-", "%", "!", "^", "~", ":"]
with open("keywords.json", encoding='utf-8') as file:
    translation_dictionary = json.loads(file.read())


class CustomText(tk.Text):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        font = tkfont.Font(font=self['font'])
        tab_size = font.measure('    ') # 4 spaces
        self.config(tabs=tab_size) # set tab size
        self.focus_set()
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


    def select_all(self):
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)

    def delete_word(self):
        self.delete("insert-1c wordstart", "insert")
        
    def toggle_comment(self):
        sel_start, sel_end = self.tag_ranges(tk.SEL)

        if sel_start and sel_end:
            selected_text = self.get(sel_start, sel_end)

            lines = selected_text.split('\n')
            is_commented = lines[0].lstrip().startswith('#')
            modified_lines = []
            ignore_empty = False
            for line in lines:
                stripped_line = line.lstrip()
                if stripped_line:  # Non-empty line
                    if is_commented and stripped_line.startswith('#'):
                        modified_lines.append(line.replace('#', '', 1))
                    elif not is_commented and not stripped_line.startswith('#'):
                        modified_lines.append('#' + line.lstrip())
                    else:
                        modified_lines.append(line)
                    ignore_empty = True
                elif ignore_empty:
                    modified_lines.append(line)

            modified_text = '\n'.join(modified_lines)
            self.delete(sel_start, sel_end)
            self.insert(sel_start, modified_text)

            # Restore the selection
            self.tag_add(tk.SEL, sel_start, f"{sel_start}+{len(modified_text)}c")
            self.tag_remove(tk.SEL, f"{sel_start}+{len(modified_text)}c", tk.END)

            return 'break'  # Prevent default behavior
        
    def move_line_up(self, event):
        text_widget = event.widget
        sel_start, sel_end = map(str, text_widget.tag_ranges(tk.SEL))
        if sel_start and sel_end:
            # Get the selected line
            start_line, _ = map(int, sel_start.split('.'))
            line_start_index = f"{start_line}.0"
            line_end_index = f"{start_line}.end"
            selected_line = text_widget.get(line_start_index, line_end_index)

            # Get the line above the selected line
            if start_line > 1:
                prev_line_index = f"{start_line - 1}.0"
                prev_line_end_index = f"{start_line - 1}.end"
                prev_line = text_widget.get(prev_line_index, prev_line_end_index)
            else:
                prev_line = ""  # Empty line to prevent shifting above first line

            # Move the selected line up by one line
            text_widget.delete(line_start_index, line_end_index)
            text_widget.delete(prev_line_index, prev_line_end_index)
            text_widget.insert(prev_line_index, selected_line + '\n')
            text_widget.insert(line_start_index, prev_line.rstrip('\n'))

            new_sel_start = f"{start_line - 1}.0"
            new_sel_end = f"{start_line - 1}.{len(selected_line)}"

            # Delete the extra empty line if it exists
            extra_line_index = f"{start_line}.{len(selected_line)}"
            extra_line = text_widget.get(extra_line_index, f"{start_line + 1}.0")
            if extra_line.strip() == '':
                text_widget.delete(extra_line_index, f"{start_line + 1}.0")

            # Update the selection range and move the cursor to the new line
            text_widget.tag_add(tk.SEL, new_sel_start, new_sel_end)
            text_widget.tag_remove(tk.SEL, sel_end, tk.END)
            text_widget.mark_set(tk.INSERT, new_sel_start)

            return 'break'  # Prevent default behavior
                
def start():
    global current_file
    save()

    print(f"\nСТАРТ {current_file}")
    if os.name == "nt":
        if current_file is None:
            subprocess.run(["cmd.exe", "/c", "start", f"bushmaster.{build_extension}"])

        else:
            subprocess.run(["cmd.exe", "/c", "start", f"bushmaster.{build_extension}", current_file, "-IDE"])

    else:
        if current_file is None:
            os.system(f"./bushmaster.{build_extension}")
        else:
            os.system(f"./bushmaster.{build_extension} {current_file} -IDE")

def new():
    text.delete(1.0, tk.END)
    current_file = None
    root.title(f"IDE bushmaster | {current_file}")
    print("\nНОВЫЙ ФАЙЛ")

def save():
    try:
        global current_file
        file_name = fd.asksaveasfilename(defaultextension=".bm", # .* not works on posix
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
    print(f"IDE Бушмейстер {version} - среда разработки и обучения для языка программирования Бушмейстер.")
    showinfo(title="Помощь", message=help_screen)

def docs():
    print(docs_screen)
    showinfo(title="Документация", message=docs_screen)

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

    # Hotkeys for ui
    root.bind("<Control-s>", lambda _: save()) # Save file
    root.bind("<Control-o>", lambda _: open_()) # Open file
    root.bind("<Control-n>", lambda _: new()) # Create new file
    root.bind("<F5>", lambda _: start()) # Run file
    root.bind("<F1>", lambda _: help_())

    # Hotkeys for textbox
    root.bind("<Control-a>", lambda _: text.select_all()) # Select all text in textbox
    root.bind("<Control-BackSpace>", lambda _: text.delete_word()) # Delete whole word with ctrl+backspace
    
    text.bind("<Control-slash>", lambda _: text.toggle_comment())
    text.bind("<Alt-Up>", lambda e: text.move_line_up(e))
    root.mainloop()

