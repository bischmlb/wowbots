
import webbrowser
import sys
import os
import struct
import time
import tkinter
import datetime
#
import pyautogui
import numpy as np
import cv2
import logging
#
from win10toast import ToastNotifier
from PIL import ImageGrab, Image
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect
from threading import Thread
from infi.systray import SysTrayIcon
from tkinter import *
from datetime import datetime


knownUser = {
    "admin": "admin",
}

loginFail = False


# For at kunne execute multiple commands i tkinter ..
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def app_pause(systray):
    global is_stop
    is_stop = False if is_stop is True else True
    #print("på pause (True/False): " + str(is_stop))
    if is_stop is True:
        info = "---BOT_PAUSE--- \n" + printTime() + "_BOT_ >> Sat på pause"
        print(info)
        logging.info(info)
        systray.update(
            hover_text=app + " - sat på pause")
    else:
        info = "---BOT_PAUSE--- \n" + printTime() + "_BOT_ >> Startet igen"
        print(info)
        logging.info(info)
        systray.update(
            hover_text=app)

# Lukker appen korrekt


def app_destroy(systray):
    info = "---BOT_SHUTDOWN--- \n" + printTime() + "_BOT_ >> Lukker ned ..."
    print(info)
    logging.info(info)
    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("---BOT_STATS---")
    print("Tid total: {:0>2}:{:0>2} Hours".format(int(hours), int(minutes)))
    sys.exit()


def app_about(systray):
    print(help)

# Bruges ikke til noget pt


def setFlagExit():
    print(button_start)
    button_start = True
    flag_exit = False
    print(button_start)

# UI Til opstart


def __initGUI__():
    frame = tkinter.Tk()

    w = 600
    h = 700

    ws = frame.winfo_screenwidth()
    hs = frame.winfo_screenheight()

    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    frame.geometry('%dx%d+%d+%d' % (w, h, x, y))

    frame.title('Bisches BOTS - Vælg en bot')
    frame.iconbitmap(r'fish_bot.ico')
    # label1 = Label(frame, text="(OBS: Fungerer bedst i windowed mode 800x600)", font=("Arial", 8)) - Man kan ikke reframe wow mere.
    # label1.pack()

    ansvarTxt = Label(frame, text="Disclaimer: Alt bruges på eget ansvar.", font=(
        "Arial", 8)).pack(side=TOP)
    separator1 = Label(frame, justify=LEFT, font=(
        "Arial", 12), text="________________________________________").pack()

    title1 = Label(frame, justify=LEFT, font=("Arial", 12),
                   text="Fiskermanden 1.0").pack(pady=30)
    title2 = Label(frame, justify=LEFT, font=("Arial", 10),
                   text="Scanner efter watersplash, og klikker.").pack()
    label2 = Label(frame, justify=LEFT, font=(
        "Arial", 8), text=" 1. equip fishing pole \n 2. sæt 'Fishing' som nummer 1 skill i din action bar \n 3. toggle wow UI (ALT + Z) \n 4. zoom helt ind(!!) \n 5. pause/unpause ved klik på ikon nede til højre \n").pack()

    startFishing = Button(frame,
                          font=("arial", 14),
                          command=combine_funcs(frame.destroy, runBot),
                          relief=SOLID,
                          height=2,
                          width=8,
                          text="Start").pack(side=TOP, padx=0, pady=40)

    separator2 = Label(frame, justify=LEFT, font=(
        "Arial", 12), text="________________________________________").pack()

    title3 = Label(frame, justify=LEFT, font=(
        "Arial", 12), text="Avoid AFK").pack(pady=30)
    title4 = Label(frame, justify=LEFT, font=("Arial", 10),
                   text="Undgå at blive flagged som AFK").pack()
    label3 = Label(frame, justify=LEFT, font=(
        "Arial", 8), text="Brugbar under nye releases, så du kan gå AFK uden at skulle sidde i login-que efter. \nDet er det krav, at dit hop-bind er 'space'").pack()

    startAvoidAfk = Button(frame,
                           font=("arial", 14),
                           command=combine_funcs(frame.destroy, avoidAfk),
                           relief=SOLID,
                           height=2,
                           width=8,
                           text="Start").pack(side=TOP, padx=0, pady=40)


#    forsøg på at importere et billede til gui ..
#    load = Image.open("wow-fish-bot-area.png")
#    render = ImageTk.PhotoImage(load)

#    img = Label(frame, image=render)
#    img.image = render
#    img.place(x=0,y=0)

    frame.mainloop()

# Funktion der printer aktuelle tid


def printTime():
    return "[" + datetime.now().strftime('%d-%m-%Y|%H:%M:%S') + "] "

# FISH Botten


def runBot():
    global start
    start = time.time()
    flag_exit = False
    lastx = 0
    lasty = 0
    is_block = False
    new_cast_time = 0
    recast_time = 40
    wait_mes = 0
    global fiskCount
    fiskCount = 0

    info = ""

    #--log fil. Ikke til meget brug endnu..--#
    log = "bot_logfile.log"
    logging.basicConfig(filename=log, level=logging.DEBUG,
                        format='%(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    app_ico = resource_path('fish_bot.ico')

    #Systemtray + Menu
    menu_options = (("start/stop", None, app_pause),
                    ("hjælp", None, app_about),)
    systray = SysTrayIcon(app_ico, app,
                          menu_options, on_quit=app_destroy)
    systray.start()
    info = "---BOT_START---"
    print(info)
    logging.info(info)
    toaster = ToastNotifier()
    toaster.show_toast(app,
                       "- BOT sat i gang og minimeret. \n- Botten kan nu findes og styres i system tray.",
                       icon_path=app_ico,
                       duration=5)
    # Bot kør

    # Init state for buff time stamp.
    ts_use_buff_old = 0
    # Hvis flag_exit = False kører vi i loop
    while flag_exit is False:
        if is_stop == False:
            # Tjek om WOW er det aktive vindue
            if GetWindowText(GetForegroundWindow()) != "World of Warcraft":
                if wait_mes == 10:
                    wait_mes = 0
                    toaster.show_toast(app,
                                       "Sæt venligst wow som active window, eller sæt botten på pause.",
                                       icon_path='fish_bot.ico',
                                       duration=5)
                info = printTime() + "_BOT_ >> Venter på at WOW bliver sat som active window"
                print(info)
                logging.info(info)
                systray.update(
                    hover_text=app
                    + " - venter på at WOW bliver sat som active window")
                wait_mes += 1
                time.sleep(5)
            # Hvis wow er det aktive vindue, påbegynder vi fishing
            else:
                # Check buff time left ...
                # Use if > 10 minutes (600s)
                ts_use_buff_new = time.time()
                # If diff is more than 10 minutes, we should use buff
                if ts_use_buff_new - ts_use_buff_old > 600:
                    print("_BOT_ >> Prøver at bruge buff")
                    pyautogui.press('2')
                    time.sleep(6)
                    ts_use_buff_old = ts_use_buff_new

                systray.update(hover_text=app)
                rect = GetWindowRect(GetForegroundWindow())

                # Hvis is_block = False kaster vi rod ...
                # Vi sætter is_block til true så vi ikke kaster flere rods
                if is_block == False:
                    lastx = 0
                    lasty = 0
                    pyautogui.press('1')
                    info = printTime() + "_BOT_ >> Fisker ..."
                    print(info)
                    logging.info(info)
                    new_cast_time = time.time()
                    is_block = True
                    time.sleep(2)
                # Opsætning af masken hvor vi scanner for splash effect ..
                else:
                    fish_area = (0, rect[3] / 2, rect[2], rect[3])

                    img = ImageGrab.grab(fish_area)
                    img_np = np.array(img)

                    frame = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
                    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                    h_min = np.array((0, 0, 253), np.uint8)
                    h_max = np.array((255, 0, 255), np.uint8)

                    mask = cv2.inRange(frame_hsv, h_min, h_max)

                    moments = cv2.moments(mask, 1)
                    dM01 = moments['m01']
                    dM10 = moments['m10']
                    dArea = moments['m00']

                    b_x = 0
                    b_y = 0

                    if dArea > 0:
                        b_x = int(dM10 / dArea)
                        b_y = int(dM01 / dArea)
                    if lastx > 0 and lasty > 0:
                        if lastx != b_x and lasty != b_y:
                            is_block = False
                            if b_x < 1:
                                b_x = lastx
                            if b_y < 1:
                                b_y = lasty
                            pyautogui.moveTo(b_x, b_y + fish_area[1], 0.3)
                            pyautogui.keyDown('shiftleft')
                            pyautogui.mouseDown(button='right')
                            pyautogui.mouseUp(button='right')
                            pyautogui.keyUp('shiftleft')
                            fiskCount = fiskCount + 1
                            info = printTime() + "_BOT_ >> Fisk fanget!"
                            print(info)
                            logging.info(info)
                            info = printTime() + "_BOT_ >> ~ Fangede fisk: " + str(fiskCount)
                            print(info)
                            logging.info(info)
                            time.sleep(2)
                    lastx = b_x
                    lasty = b_y

                    # show windows with mask
                    # cv2.imshow("fish_mask", mask)
                    # cv2.imshow("fish_frame", frame)

                    if time.time() - new_cast_time > recast_time:
                        # print("New cast if something wrong")
                        is_block = False
            if cv2.waitKey(1) == 27:
                break
        else:
            info = printTime() + \
                "_BOT_ >> Botten er sat på pause - venter på at der bliver trykket start ..."
            print(info)
            logging.info(info)
            systray.update(hover_text=app + " - på pause")
            time.sleep(6)


def avoidAfk():
    global start
    start = time.time()
    flag_exit = False
    hopCount = 0
    is_block = False
    wait_mes = 0

    info = ""

    #--log fil. Ikke til meget brug endnu..--#
    log = "bot_logfile.log"
    logging.basicConfig(filename=log, level=logging.DEBUG,
                        format='%(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    app_ico = resource_path('fish_bot.ico')

    #Systemtray + Menu
    menu_options = (("start/stop", None, app_pause),
                    ("hjælp", None, app_about),)
    systray = SysTrayIcon(app_ico, app,
                          menu_options, on_quit=app_destroy)
    systray.start()
    info = "---BOT_START---"
    print(info)
    logging.info(info)
    toaster = ToastNotifier()
    toaster.show_toast(app,
                       "- BOT sat i gang og minimeret. \n- Botten kan nu findes og styres i system tray.",
                       icon_path=app_ico,
                       duration=5)
    # Bot kør
    # Hvis flag_exit = False kører vi i loop
    while flag_exit is False:
        if is_stop == False:
            # Tjek om WOW er det aktive vindue
            if GetWindowText(GetForegroundWindow()) != "World of Warcraft":
                if wait_mes == 10:
                    wait_mes = 0
                    toaster.show_toast(app,
                                       "Sæt venligst wow som active window, eller sæt botten på pause.",
                                       icon_path='fish_bot.ico',
                                       duration=5)
                info = printTime() + "_BOT_ >> Venter på at WOW bliver sat som active window"
                print(info)
                logging.info(info)
                systray.update(
                    hover_text=app
                    + " - venter på at WOW bliver sat som active window")
                wait_mes += 1
                time.sleep(5)
            # Hvis wow er det aktive vindue, påbegynder vi avoid AFK process
            else:
                systray.update(hover_text=app)
                rect = GetWindowRect(GetForegroundWindow())

                # Hvis is_block = False hopper vi for at prevente afk...
                # Vi sætter is_block til false, og hopper først igen  om 250s.
                if is_block == False:
                    pyautogui.press('space')
                    hopCount += 1
                    info = printTime() + "_BOT_ >> Hopper ..."
                    print(info)
                    print(printTime() + "_BOT_ >> Undgik AFK " +
                          str(hopCount) + " gange")
                    logging.info(info)
                    is_block = True
                    # Hop for hvert 280s. Auto AFK = 300 (5min)
                    time.sleep(280)
                # Opsætning af masken hvor vi scanner for splash effect ..
                else:
                    is_block = False

            if cv2.waitKey(1) == 27:
                break
        else:
            info = printTime() + \
                "_BOT_ >> Botten er sat på pause - venter på at der bliver trykket start ..."
            print(info)
            logging.info(info)
            systray.update(hover_text=app + " - på pause")
            time.sleep(6)


def loginFrameCreate():

    global loginFrame
    loginFrame = tkinter.Tk()

    w = 400
    h = 285

    ws = loginFrame.winfo_screenwidth()
    hs = loginFrame.winfo_screenheight()

    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)

    loginFrame.geometry('%dx%d+%d+%d' % (w, h, x, y))

    loginFrame.title('Bisches BOTS - Login')
    loginFrame.iconbitmap(r'fish_bot.ico')

    logintitle = Label(
        loginFrame, text="Bisches BOTS - Login", font=("arial", 14))
    logintitle.pack(side=TOP, padx=0, pady=10)

    global username
    username = Entry(loginFrame,
                     relief=SOLID,
                     justify=CENTER,
                     font=("arial", 12))
    username.insert(0, "username")
    username.bind("<FocusIn>", lambda args: username.delete('0', 'end'))
    username.pack(side=TOP, padx=0, pady=25)

    global password
    password = Entry(loginFrame,
                     relief=SOLID,
                     justify=CENTER,
                     font=("arial", 12))
    password.insert(0, "password")
    password.config(show="")
    password.bind("<FocusIn>", lambda args: password.delete('0', 'end'))
    password.config(show="*")
    password.pack(side=TOP, padx=0, pady=0)
    label2 = Label(
        loginFrame, text="Hvis du mangler en bruger, kontakt bisch på discord.", font=("arial", 10))
    label2.pack(side=TOP, padx=0, pady=10)

    if loginFail == True:
        label1 = Label(
            loginFrame, text="forkert brugernavn/password, prøv igen", font=("arial", 10), fg="red")
        label1.pack(side=TOP, padx=0, pady=10)

    loginBtn = Button(loginFrame,
                      font=("arial", 16),
                      command=getUser,
                      relief=SOLID,
                      text="start").pack(side=BOTTOM, padx=0, pady=30)
    loginFrame.mainloop()


def getUser():
    user = username.get()
    passw = password.get()
    if user in knownUser:
        if knownUser[user] == passw:
            loginFrame.destroy()
            __initGUI__()
        else:
            global loginFail
            loginFail = True
            loginFrame.destroy()
            loginFrameCreate()
    else:
        loginFail = True
        loginFrame.destroy()
        loginFrameCreate()


##pyinstaller.exe --windowed --icon=fish_bot.ico bot.py##
if __name__ == "__main__":
    start = time.time()

    with open('bot_logfile.log', 'w'):
        pass

    is_stop = False
    app = "Bisches BOTS"
    help = "opsætning:\n (OBS: Fungerer bedst i windowed mode 800x600 !!) \n 1 - equip fishing pole \n 2 - sæt 'Fishing' som nummer 1 skill i din action bar \n 3 - toggle wow UI (ALT + Z) \n 4 - zoom helt ind(!!) \n 5 - pause/unpause ved klik på ikon nede til højre \n"

    __initGUI__()
