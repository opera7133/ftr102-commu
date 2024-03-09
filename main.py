import serial
import time
import sys
import glob
import os
import flet as ft
import jaconv
import pyaudio
import numpy as np
from pykakasi import kakasi

kakasi = kakasi()
global receive_break
receive_break = False


def get_serial_port():
    if sys.platform == "linux" or sys.platform == "linux2":
        ports = glob.glob('/dev/tty.usbserial*')
    elif sys.platform == "darwin":
        ports = glob.glob('/dev/tty.usbserial*')
    elif sys.platform == "win32":
        ports = ['COM%s' % (i + 1) for i in range(256)]
    else:
        raise Exception("Unsupported platform")
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def convert_to_morse_code(text: str, lang="en"):
    if lang == "ja":
        morse_code = {
            'あ': '--.--', 'い': '.-', 'う': '..-', 'え': '-.---', 'お': '.-...', 'か': '.-..', 'き': '-.-..', 'く': '...-', 'け': '-.--', 'こ': '----',
            'さ': '-.-.-', 'し': '--.-.', 'す': '---.-', 'せ': '.---.', 'そ': '---.', 'た': '-.', 'ち': '..-.', 'つ': '.--.', 'て': '.-.--', 'と': '..-..',
            'な': '.-.', 'に': '-.-.', 'ぬ': '....', 'ね': '--.-', 'の': '..--', 'は': '-...', 'ひ': '--..-', 'ふ': '--..', 'へ': '.', 'ほ': '-..',
            'ま': '-..-', 'み': '..-.-', 'む': '-', 'め': '-...-', 'も': '-..-.', 'や': '.--', 'ゆ': '-..--', 'よ': '--',
            'ら': '...', 'り': '--.', 'る': '-.--.', 'れ': '---', 'ろ': '.-.-', 'わ': '-.-', 'を': '.---', 'ん': '.-.-.',
            '゛': '..', '゜': '..--.', 'ー': '.--.-', '、': '.-.-.-', '（': '-.--.-', '）': '.-..-.', ' ': "  "
        }
        morse_code_text = ""
        for char in text:
            if char in morse_code:
                morse_code_text += morse_code[jaconv.kata2hira(char)] + " "
        return morse_code_text
    else:
        morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
            'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
            'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
            '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
            ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-', " ": "  "
        }
        morse_code_text = ""
        for char in text:
            if char.upper() in morse_code:
                morse_code_text += morse_code[char.upper()] + " "
        return morse_code_text


def convert_hex_to_morse_code(hex: str):
    morse_code = {
        '0': '-', '1': '.', "2": '.-', '3': '..', '4': '.--', '5': '.-.', '6': '..-', '7': '...',
        '8': '.---', '9': '.--.', 'A': '.-.-', 'B': '.-..', 'C': '..--', 'D': '..-.', 'E': '...-', 'F': '....',
    }
    morse_code_text = ""
    for char in hex:
        if char.upper() in morse_code:
            morse_code_text += morse_code[char.upper()] + " "
        else:
            morse_code_text += " "
    return morse_code_text


def convert_morse_to_text(morse: str, lang="en"):
    if lang == "ja":
        morse_code = {
            '--.--': 'あ', '.-': 'い', '..-': 'う', '-.---': 'え', '.-...': 'お', '.-..': 'か', '-.-..': 'き', '...-': 'く', '-.--': 'け', '----': 'こ',
            '-.-.-': 'さ', '--.-.': 'し', '---.-': 'す', '.---.': 'せ', '---.': 'そ', '-.': 'た', '..-.': 'ち', '.--.': 'つ', '.-.--': 'て', '..-..': 'と',
            '.-.': 'な', '-.-.': 'に', '....': 'ぬ', '--.-': 'ね', '..--': 'の', '-...': 'は', '--..-': 'ひ', '--..': 'ふ', '.': 'へ', '-..': 'ほ',
            '-..-': 'ま', '..-.-': 'み', '-': 'む', '-...-': 'め', '-..-.': 'も', '.--': 'や', '-..--': 'ゆ', '--': 'よ',
            '...': 'ら', '--.': 'り', '-.--.': 'る', '---': 'れ', '.-.-': 'ろ', '-.-': 'わ', '.---': 'を', '.-.-.': 'ん',
            '..': '゛', '..--.': '゜', '.--.-': 'ー', '.-.-.-': '、', '-.--.-': '（', '.-..-.': '）', "": " "
        }
        morse_text = ""
        for char in morse.split(" "):
            if char in morse_code:
                morse_text += morse_code[char]
        return morse_text
    elif lang == "en":
        morse_code = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z',
            '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9', '-----': '0',
            '--..--': ',', '.-.-.-': '.', '..--..': '?', '-..-.': '/', '-....-': '-', '-.--.': '(', '-.--.-': ')', "": " "
        }
        morse_text = ""
        for char in morse.split(" "):
            if char in morse_code:
                morse_text += morse_code[char]
        return morse_text
    else:
        morse_code = {
            '-': '0', '.': '1', '.-': '2', '..': '3', '.--': '4', '.-.': '5', '..-': '6', '...': '7',
            '.---': '8', '.--.': '9', '.-.-': 'A', '.-..': 'B', '..--': 'C', '..-.': 'D', '...-': 'E', '....': 'F',
        }
        morse_text = ""
        for char in morse.split(" "):
            if char in morse_code:
                morse_text += morse_code[char]
        return morse_text


def main(page: ft.Page):
    page.title = "FTR-102 通信"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # ----- モールス -----
    t = ft.Text()
    sendText = ft.TextField(
        label="メッセージ",
        multiline=True,
        min_lines=1,
    )
    sendText.border_color = ft.colors.WHITE
    speed = ft.Slider(
        label="{value}%",
        min=0,
        max=100,
        divisions=10,
        value=50,
    )
    lang = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="ja", label="和文"),
        ft.Radio(value="en", label="欧文"),
    ]), value="en")
    langReceive = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="ja", label="和文"),
        ft.Radio(value="en", label="欧文"),
        ft.Radio(value="bin", label="バイナリ"),
    ]), value="en")
    receiveMorse = ft.TextField(
        label="受信信号",
        multiline=True,
        min_lines=1,
        read_only=True,
    )
    receiveText = ft.TextField(
        label="受信メッセージ",
        multiline=True,
        min_lines=1,
        read_only=True,
    )

    def receive_stop(e):
        global receive_break
        receive_break = True
        receiveStop.disabled = True
        page.update()
    receiveStop = ft.ElevatedButton(
        text="停止", on_click=receive_stop, disabled=True)

    def start_receive(e):
        global receive_break
        global stop
        stop = False
        receiveStop.disabled = False
        page.update()
        print("Receiving message...")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                        rate=44100, input=True, frames_per_buffer=1024)
        send_sec = 0
        space_sec = 0
        while True:
            if receive_break:
                print("Receiving stopped")
                break
            data = stream.read(1024)
            x = np.frombuffer(data, dtype="int16") / 32768.0
            if x.max() <= 0.03 and send_sec == 0 and space_sec > 1.25:
                break
            if x.max() > 0.03:
                send_sec += 10 / 441
            elif send_sec > 0:
                if send_sec >= 0.3 * (1 / (speed.value / 50)):
                    receiveMorse.value += "-"
                    page.update()
                elif send_sec >= 0.1 * (1 / (speed.value / 50)):
                    receiveMorse.value += "."
                    page.update()
                send_sec = 0
                space_sec = 0
            else:
                space_sec += 10 / 441
                if space_sec > 0.15 * (1 / (speed.value / 50)) and len(receiveMorse.value) != 0:
                    if len(receiveMorse.value) > 2:
                        if receiveMorse.value[-2] == " ":
                            continue
                    receiveMorse.value += " "
                    page.update()
                    space_sec = 0
        stream.stop_stream()
        stream.close()
        p.terminate()
        receiveText.value = convert_morse_to_text(
            receiveMorse.value, langReceive.value)
        receiveStop.disabled = True
        print("Received message")
        page.update()
        receive_break = False

    def close_page(e):
        global receive_break
        receive_break = True
        page.update()

    def clear_receive(e):
        receiveText.value = ""
        receiveMorse.value = ""
        page.update()
    receiveText.border_color = ft.colors.WHITE
    receiveMorse.border_color = ft.colors.WHITE
    receiveClear = ft.ElevatedButton(text="クリア", on_click=clear_receive)

    receiveStart = ft.ElevatedButton(
        text="開始", on_click=start_receive)

    global stop
    stop = False

    def send(e):
        print("Sending message")
        global stop
        stop = False
        stop_button.disabled = False
        page.update()
        converted = kakasi.convert(sendText.value)
        message = list()
        for char in converted:
            message += list(char['hira'])
        port = get_serial_port()
        if len(port) == 0:
            print("No serial port found")
            return
        read = serial.Serial(port[0], 9600, dsrdtr=False)
        read.dtr = False
        time.sleep(1)
        for char in message:
            if stop:
                stop = False
                break
            encoded = convert_to_morse_code(char, lang.value)
            print(f"Sending {char} as {encoded}")
            for signal in encoded:
                if stop:
                    break
                if signal == ".":
                    read.dtr = True
                    time.sleep(0.1 * (1 / (speed.value / 50)))
                    read.dtr = False
                    time.sleep(0.05 * (1 / (speed.value / 50)))
                elif signal == "-":
                    read.dtr = True
                    time.sleep(0.3 * (1 / (speed.value / 50)))
                    read.dtr = False
                    time.sleep(0.05 * (1 / (speed.value / 50)))
                else:
                    time.sleep(0.15 * (1 / (speed.value / 50)))
        sendText.value = ""
        read.close()
        print("Message sent")
        page.update()

    sendButton = ft.ElevatedButton(text="送信", on_click=send)
    # ----- バイナリ -----
    global file_path
    file_path = ""

    def send_binary(e):
        global file_path
        global stop
        stop = False
        stop_button.disabled = False
        page.update()
        if (file_path == ""):
            print("No file selected")
            return
        print("Sending binary")
        port = get_serial_port()
        if len(port) == 0:
            print("No serial port found")
            return
        read = serial.Serial(port[0], 9600, dsrdtr=False)
        read.dtr = False
        time.sleep(1)
        file_size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            byte = f.read(file_size)
            hex_data = byte.hex()
            read_bytes = 0
            for i in range(0, len(hex_data), 2):
                if stop:
                    stop = False
                    break
                progress.value = read_bytes / len(hex_data)
                page.update()
                encoded = convert_hex_to_morse_code(hex_data[i:i+2])
                print(f"Sending {hex_data[i:i+2]} as {encoded}")
                for signal in encoded:
                    if signal == ".":
                        read.dtr = True
                        time.sleep(0.1 * (1 / (speed.value / 50)))
                        read.dtr = False
                        time.sleep(0.05 * (1 / (speed.value / 50)))
                    elif signal == "-":
                        read.dtr = True
                        time.sleep(0.3 * (1 / (speed.value / 50)))
                        read.dtr = False
                        time.sleep(0.05 * (1 / (speed.value / 50)))
                    else:
                        time.sleep(0.15 * (1 / (speed.value / 50)))
                read_bytes += 1
        read.close()
        print("Binary sent")
        page.update()

    def set_file_name(e):
        file_name.value = e.files[0].name
        global file_path
        file_path = e.files[0].path
        page.update()

    def stop_send(e):
        global stop
        stop = True
        stop_button.disabled = True
    file_picker = ft.FilePicker(
        on_result=set_file_name)
    page.overlay.append(file_picker)
    file_name = ft.Text()
    pick_button = ft.ElevatedButton(
        text="ファイルを選択", on_click=lambda e: file_picker.pick_files(allow_multiple=False))
    progress = ft.ProgressBar()
    send_button = ft.ElevatedButton(text="送信", on_click=send_binary)
    stop_button = ft.ElevatedButton(
        text="停止", on_click=stop_send, disabled=True)

    info = """#### **FTR-102 通信プログラム**

このプログラムは、FTR-102を使用してモールス信号やバイナリデータを送受信するためのプログラムです。

バージョン: 1.0

開発者: [wamo](https://github.com/opera7133)
"""

    pages = [
        [ft.Text("速度", size=20),
         speed, ft.Text("言語", size=20), lang, ft.Text("メッセージ", size=20), sendText, sendButton, stop_button, t],
        [ft.Text("速度", size=20),
         speed, ft.Text("バイナリ", size=20),
         ft.Row([pick_button, file_name], spacing=5), progress, send_button, stop_button],
        [ft.Text("受信", size=20), speed, ft.Text("言語", size=20), langReceive, receiveMorse, receiveText, ft.Row(
            [receiveStart, receiveStop, receiveClear], spacing=5)],
        [ft.Text("情報", size=20), ft.Markdown(
            info, on_tap_link=lambda e: page.launch_url(e.data),)]
    ]

    current_page = pages[0]

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Row([rail, ft.VerticalDivider(width=1), ft.Column(
                        current_page, expand=True)], expand=True)
                ]
            )
        )
        if page.route == "/binary":
            page.views[0] = ft.View(
                "/binary",
                [
                    ft.Row([rail, ft.VerticalDivider(width=1), ft.Column(
                        pages[1], expand=True)], expand=True)
                ]
            )
        if page.route == "/receive":
            page.views[0] = ft.View(
                "/receive",
                [
                    ft.Row([rail, ft.VerticalDivider(width=1), ft.Column(
                        pages[2], expand=True)], expand=True)
                ]
            )
        if page.route == "/info":
            page.views[0] = ft.View(
                "/info",
                [
                    ft.Row([rail, ft.VerticalDivider(width=1), ft.Column(
                        pages[3], expand=True)], expand=True)
                ]
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def change_page(e: ft.ControlEvent):
        page.go(f"/{['', 'binary', 'receive', 'info'][int(e.data)]}")

    rail = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.icons.MORE_HORIZ_OUTLINED,
                selected_icon=ft.icons.MORE_HORIZ,
                label="モールス",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.CODE_OUTLINED,
                selected_icon=ft.icons.CODE,
                label="バイナリ",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.CLOUD_DOWNLOAD_OUTLINED,
                selected_icon=ft.icons.CLOUD_DOWNLOAD,
                label="受信",
            ),
            ft.NavigationRailDestination(
                icon=ft.icons.INFO_OUTLINED,
                selected_icon=ft.icons.INFO,
                label="情報",
            ),
        ],
        label_type=ft.NavigationRailLabelType.ALL,
        selected_index=0,
        on_change=change_page,
    )
    theme = ft.Theme()
    theme.page_transitions.macos = ft.PageTransitionTheme.NONE
    theme.page_transitions.windows = ft.PageTransitionTheme.NONE
    page.theme = theme
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
    page.on_close = close_page


ft.app(target=main)
