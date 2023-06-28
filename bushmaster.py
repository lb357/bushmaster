import datetime
import os
import sys
import re
import subprocess
import math
import json

version = "1.0"

welcome_screen = \
    f"""{"=" * (len(os.getcwd()) // 2 + 5)} Бушмейстер {version} {"=" * (len(os.getcwd()) // 2 + 5)}
Время запуска: {datetime.datetime.now()}
Запуск из каталога: {os.getcwd()}
ОС: {os.name}
Запуск основного скрипта в IDE: {not (sys.stdin.isatty())}
Введите "справка" или "документация" для получения большей информации.
{"=" * (len(os.getcwd()) + len(version) + 23)}\n"""

help_screen = \
    f"""Бушмейстер {version} - высокоуровневый русскоязычный язык программирования, транслирующийся в Python.
Leonid Briskindov / RobotX / 2023 ( https://github.com/lb357/bushmaster )
"""

docs_screen = \
    """Для получения документации см. каталог docs в корневой папке
"""

is_stop = False
with open("keywords.json", encoding='utf-8') as file:
    translation_dictionary = json.loads(file.read())


def translate(input_data: str) -> str:
    output_data = input_data
    start_output_data_sting_split_1 = re.split(r"""[']""", output_data)
    start_output_data_sting_split_2 = re.split(r"""["]""", output_data)
    for old, new in translation_dictionary.items():
        output_data = re.sub(rf'\b{old}\b', new, output_data)
    end_output_data_sting_split = re.split(r"""[']""", output_data)
    for index in range(len(end_output_data_sting_split)):
        if index % 2 != 0 and len(end_output_data_sting_split) != 0:
            end_output_data_sting_split[index] = "'" + str(start_output_data_sting_split_1[index]) + "'"
    end_output_data_sting_split = re.split(r"""["]""", output_data)
    for index in range(len(end_output_data_sting_split)):
        if index % 2 != 0 and len(end_output_data_sting_split) != 0:
            end_output_data_sting_split[index] = '"' + str(start_output_data_sting_split_2[index]) + '"'
    output_data = ""
    for data in end_output_data_sting_split:
        output_data += str(data)
    return output_data


def retranslate(input_data: str) -> str:
    output_data = input_data
    start_output_data_sting_split_1 = re.split(r"""[']""", output_data)
    start_output_data_sting_split_2 = re.split(r"""["]""", output_data)
    for new, old in translation_dictionary.items():
        output_data = re.sub(rf'\b{old}\b', new, output_data)
    end_output_data_sting_split = re.split(r"""[']""", output_data)
    for index in range(len(end_output_data_sting_split)):
        if index % 2 != 0 and len(end_output_data_sting_split) != 0:
            end_output_data_sting_split[index] = "'" + str(start_output_data_sting_split_1[index]) + "'"
    end_output_data_sting_split = re.split(r"""["]""", output_data)
    for index in range(len(end_output_data_sting_split)):
        if index % 2 != 0 and len(end_output_data_sting_split) != 0:
            end_output_data_sting_split[index] = '"' + str(start_output_data_sting_split_2[index]) + '"'
    output_data = ""
    for data in end_output_data_sting_split:
        output_data += str(data)
    return output_data


def pause():
    try:
        if os.name == "nt" and sys.stdin.isatty():
            subprocess.Popen("pause", shell=True)
        elif os.name == "posix" and sys.stdin.isatty():
            subprocess.Popen("read –n1", shell=True)
        else:
            input("Для продолжения осуществите ввод . . . ")
    except:
        print("ПАУЗА")



def import_bm(file_name: str):
    with open(f"{file_name}.bm", encoding='utf-8') as file:
        try:
            exec(translate(file.read()))
        except Exception as error:
            print("Ошибка:", error)


def exec_bm(script: str):
    exec(translate(script))


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print(welcome_screen)
        while not is_stop:
            input_data = input(">>> ")
            if input_data == "справка":
                print(help_screen)
            elif input_data == "документация":
                print(docs_screen)
            else:
                try:
                    exec(translate(input_data))
                except Exception as error:
                    print("Ошибка:", error)
    else:
        with open(sys.argv[1], encoding='utf-8') as file:
            try:
                if "-IDE" in sys.argv:
                    print(f"{welcome_screen}\n\n\n")
                exec(translate(file.read()))
            except Exception as error:
                print("Ошибка:", error)
                if "-IDE" in sys.argv:
                    pause()