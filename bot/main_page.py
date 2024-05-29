#region LIBRARY
# Tkinter ve GUI ile ilgili kütüphaneler
import customtkinter
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter.filedialog
from tkinter import messagebox

# Resim işleme ve dosya işlemleri için kütüphaneler
import os
from PIL import Image
import subprocess
import atexit
import psutil
# Selenium ve web scraping ile ilgili kütüphaneler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
#from selenium.common.exceptions import StaleElementReferenceException

# Logging ile ilgili kütüphaneler
import logging

# Zaman işlemleri ve threading için kütüphaneler
import time
import threading

# JSON işlemleri için kütüphane
import json

# Tarih ve saat işlemleri için kütüphane
from datetime import datetime, timedelta
import ntplib

# Dosya işlemleri için kütüphane
import shutil
import sys
from cryptography.fernet import Fernet
import signal
#endregion

# region Class
    #region ScrollableRadiobuttonFrame
class ScrollableRadiobuttonFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, radio_type, command=None, username=None, **kwargs):
        super().__init__(master, **kwargs)

        self.id = username
        self.command = command
        self.radiobutton_variable = customtkinter.StringVar()
        self.radiobutton_list = []
        self.create_radio_buttons_backups(radio_type)

    def initialize_backup_info(self):
            backup_folder = "backup_info"
            if not os.path.exists(backup_folder):
                os.mkdir(backup_folder)

            self.info_file_path = os.path.join(backup_folder, "backup_info.json")

            try:
                # JSON dosyasını açın ve mevcut yedekleme bilgilerini yükleyin
                with open(self.info_file_path, "r") as json_file:
                    backup_info = json.load(json_file)
            except FileNotFoundError:
                # Dosya bulunamazsa, yeni bir JSON dosyası oluşturun
                backup_info = []
                with open(self.info_file_path, "w") as new_json_file:
                    json.dump(backup_info, new_json_file)

            return backup_info

    def add_item(self, item):
        radiobutton = customtkinter.CTkRadioButton(self, text=item, value=item, variable=self.radiobutton_variable)
        if self.command is not None:
            radiobutton.configure(command=self.command)
        radiobutton.grid(row=len(self.radiobutton_list), column=0, pady=(0, 10), sticky="w")
        self.radiobutton_list.append(radiobutton)

    def create_radio_buttons_backups(self, radio_type):
        backups = self.get_backups(radio_type)
        for backup in backups:
            self.add_item(backup)

    def get_backups(self, radio_type):
        backup_info = self.initialize_backup_info()

        if self.id is not None:
            backups = [entry["file_name"] for entry in backup_info if entry.get("id") == self.id and (entry["status"] == "done" if radio_type == 0 else entry["status"] != "done")]
        else:
            backups = []

        return backups
    
    def refresh_backup_list(self, radio_type):
        # Mevcut radio buttons'ları temizle
        for radiobutton in self.radiobutton_list:
            radiobutton.destroy()
        self.radiobutton_list.clear()

        # Yeniden oluştur
        backups = self.get_backups(radio_type)
        for backup in backups:
            self.add_item(backup)

    def get_checked_item(self):
        return self.radiobutton_variable.get()
    
    def deselect(self):
        self.radiobutton_variable.set(None)

    '''''
    def remove_item(self, item):
        for radiobutton in self.radiobutton_list:
            if item == radiobutton.cget("text"):
                radiobutton.destroy()
                self.radiobutton_list.remove(radiobutton)
                return
    
    def get_backup_info(self):

        backup_folder = "backup_info"
        if not os.path.exists(backup_folder):
            os.mkdir(backup_folder)

        self.info_file_path = os.path.join(backup_folder, "backup_info.json")

        try:
            # JSON dosyasını açın ve mevcut yedekleme bilgilerini yükleyin
            with open(self.info_file_path, "r") as json_file:
                backup_info = json.load(json_file)
        except FileNotFoundError:
            # Dosya bulunamazsa, yeni bir JSON dosyası oluşturun
            backup_info = []
            with open(self.info_file_path, "w") as new_json_file:
                json.dump(backup_info, new_json_file)

        return backup_info

    def create_radio_buttons_backups(self,radio_type):
        if radio_type==0:
            backups = self.get_backups_done()
        else: 
            backups = self.get_backups_undone()

        for backup in backups:
            self.add_item(backup)

    def get_backups_done(self):

        backup_info = self.get_backup_info()
        backups = [entry["file_name"] for entry in backup_info if entry["status"] == "done"]
        return backups

    def get_backups_undone(self):
        backup_info = self.get_backup_info()
        backups = [entry["file_name"] for entry in backup_info if entry["status"] != "done"]
        return backups
    '''''

    #endregion
#endregion

class MainPage(customtkinter.CTk):
#region UI
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        #yeni
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.close_All)

        #####-VALUES-Global-#####
        self.log_folder = 'logs'  # Log dosyalarını farklı bir klasöre yerleştirin
        self.key_file = "fernet_key.key"
        self.encrypted_credentials_file = "encrypted_credentials.json"
        #self.group_index_lock = threading.Lock()
        self.radio_name=None

        #####-LOG-#####
        self.log_setting()

        # Anahtar dosyasını kontrol et
        if self.check_key_file():
            # Anahtar dosyası yoksa yeni bir anahtar oluştur
          self.key = self.load_key()
          self.cipher_suite = Fernet(self.key)

        # sys.argv[1] burada 'str(id)' değeri olacaktır
        self.username = sys.argv[1] if len(sys.argv) > 1 else None

        if not self.username:         
            self.close_app()

        self.left = self.get_user_left_date()  # self.left'ı al
        #self.left = datetime.strptime(self.left, "%Y-%m-%d")  # self.left stringini datetime nesnesine dönüştür
        self.left = datetime.strptime(self.left, "%Y-%m-%d %H:%M:%S")   
        self.left_date=self.left.strftime("%Y-%m-%d %H")

        #self.left = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M:%S") if len(sys.argv) > 2 else None

        '''
        # En az 2 argüman bekliyoruz: main_page.py ve tarih
        if len(sys.argv) > 2:
            left_str = sys.argv[2]
            self.left = datetime.strptime(left_str, "%Y-%m-%d %H:%M:%S")
        else:
            # Eğer tarih bilgisi gelmezse, self.left değerini None olarak ayarla
            self.left = None
        '''
        
        self.file_path=None
        self.lines =None
        self.login_mode="half" #Half Full
        self.web_mode="normal" #Normal Hide
        self.bot_mode="fast" #Fast Normal
        self.test_mode=False #True False

        self.backup_file_folder = "backup_file"
        self.backup_info_folder = "backup_info"
        self.is_group_operation=True
        self.is_multi_option=False
        self.group_size=4
        self.try_count=2
        self.f=False
        self.f_2=False

#####-UI-#####
        self.title("Easy Bot SporToto")

        self.default_width = 1400
        self.default_height = 800
        self.current_scaling = 100

        # Set default geometry
        self.geometry(f"{self.default_width}x{self.default_height}")
        self.resizable(0, 0)  # X and Y dimensions cannot be changed
        #region Head
        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "CustomTkinter_logo_single.png")), size=(26, 26))
        self.large_test_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "large_test_image.png")), size=(500, 150))
        self.image_icon_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "image_icon_light.png")), size=(20, 20))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "add_user_light.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="  Image Example", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Giriş ve Bilgilendirme",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.frame_2_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="İşlemler",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.chat_image, anchor="w", command=self.frame_2_button_event)
        self.frame_2_button.grid(row=2, column=0, sticky="ew")

        self.frame_3_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="İşlem Geçmişi",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.add_user_image, anchor="w", command=self.frame_3_button_event)
        self.frame_3_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_label = customtkinter.CTkLabel(self.navigation_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        # self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=20, sticky="s")
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

        self.scaling_label = customtkinter.CTkLabel(self.navigation_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.navigation_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        #endregion

        #region Create Home Frame
        # Create Home Frame
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight=1)

        self.home_frame_large_image_label = customtkinter.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        self.home_frame_large_image_label.grid(row=0, column=0, columnspan=2, padx=20, pady=5)
            
        # BOT HAKKINDA Row=1 Column=0
        self.textbox_frame = customtkinter.CTkScrollableFrame(self.home_frame, label_text="BOT HAKKINDA", width=550, height=550, orientation="horizontal")
        self.textbox_frame.grid(row=1, column=0, padx=(20, 20), pady=(5, 20), sticky="")
        self.textbox_frame.grid_columnconfigure(0, weight=1) 
        # textbox
        self.textbox = customtkinter.CTkTextbox(self.textbox_frame, width=530, height=530)
        self.textbox.grid(row=0, column=0, padx=(10, 0), pady=(0, 0), sticky="")

        # GUVENLIK VE SORUMLULKLAR Row=1 Column=1
        self.textbox2_frame = customtkinter.CTkScrollableFrame(self.home_frame, label_text="GUVENLIK VE SORUMLULKLAR", width=550, height=550, orientation="horizontal")
        self.textbox2_frame.grid(row=1, column=1, padx=(20, 20), pady=(5, 20), sticky="")
        self.textbox2_frame.grid_columnconfigure(0, weight=1)
        # textbox
        self.textbox2 = customtkinter.CTkTextbox(self.textbox2_frame, width=530, height=530)
        self.textbox2.grid(row=0, column=0, padx=(10, 0), pady=(0, 0), sticky="")
    #endregion

        #region Create Bot Frame
        # Create Bot Frame
        self.second_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.second_frame.grid_columnconfigure(1, weight=1)

        # Head İmage Row=0 Column=0 Columnspan=3
        self.Bot_frame_large_image_label = customtkinter.CTkLabel(self.second_frame, text="", image=self.large_test_image)
        self.Bot_frame_large_image_label.grid(row=0, column=0,columnspan=4, padx=0, pady=0)


        # STEPS Row=1 Column=0
        self.STEPS_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="Adımlar", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"), height=570,width=230)
        self.STEPS_frame.grid(row=1, column=0, rowspan=2, padx=(30, 0), pady=(0, 0), sticky="")
        self.STEPS_frame.grid_columnconfigure(0, weight=1)
        
        self.label_LEFT = customtkinter.CTkLabel(self.STEPS_frame, text=f"Üyelik Bitiş Tarihi: {self.left_date}",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#919599"),width=150, corner_radius=8)
        self.label_LEFT.grid(row=0, column=0, pady=(15, 15), padx=(18,0), sticky="")

        self.checkbox_file_control = customtkinter.CTkCheckBox(master=self.STEPS_frame,text="Dosya Seçildi mi?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_file_control.grid(row=1, column=0, pady=(15, 30), padx=(0,0), sticky="w")
        self.checkbox_progress_control = customtkinter.CTkCheckBox(master=self.STEPS_frame,text="İşlem Yöntemleri!",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_progress_control.grid(row=2, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_logincontrol_control = customtkinter.CTkCheckBox(master=self.STEPS_frame,text="LOGIN Olundu mu?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_logincontrol_control.grid(row=3, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_login_control = customtkinter.CTkCheckBox(master=self.STEPS_frame,text="LOGIN Kontrol Sağlandı mı?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_login_control.grid(row=4, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_bot_control = customtkinter.CTkCheckBox(master=self.STEPS_frame,text="BOT Başlatıldı!",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_bot_control.grid(row=5, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_finish_control = customtkinter.CTkCheckBox(master=self.STEPS_frame,text="Bot İşlemleri Bitti",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_finish_control.grid(row=6, column=0, pady=(30, 30), padx=(0,0), sticky="w")


        # Select File Row=1 Column=1
        self.SELECT_FILE_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="Dosya Seç", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.SELECT_FILE_frame.grid(row=1, column=1, padx=(65, 30), pady=(0, 50), sticky="")
        self.SELECT_FILE_frame.grid_columnconfigure(0, weight=1)

        self.dragdropbutton = customtkinter.CTkButton(self.SELECT_FILE_frame, text="Dosya Sürükle Bırak" ,width=200, height=90,command=self.drag_drop_window_btn)
        self.dragdropbutton.grid(row=0, column=0, padx=(15,0),pady=(15,0),sticky="")
        self.label_or = customtkinter.CTkLabel(self.SELECT_FILE_frame, text="Veya",font=customtkinter.CTkFont(size=10, weight="bold"))
        self.label_or.grid(row=1, padx=(15,0),pady=(5,0), column=0,sticky="")
        self.file_button = customtkinter.CTkButton(self.SELECT_FILE_frame,text="Dosya Seç", command=self.select_file_btn)
        self.file_button.grid(row=3, column=0, padx=(15,0), pady=(5,0))
        self.checkbox_File_control = customtkinter.CTkCheckBox(master=self.SELECT_FILE_frame,text="Selected File?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_File_control.grid(row=4, column=0, pady=(30, 5), padx=(10,5), sticky="sw")

        # PROGRESS Row=1 Column=2
        self.PROGRESS_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="İşlem Yöntemi (İsteğe Bağlı)", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.PROGRESS_frame.grid(row=1, column=2, padx=(30, 70), pady=(0, 50), sticky="")
        self.PROGRESS_frame.grid_columnconfigure(0, weight=1)

        self.radio_var = tkinter.IntVar(value=0)
        self.label_bot_type = customtkinter.CTkLabel(master=self.PROGRESS_frame, text="--  Bot Tipi Seç  --")
        self.label_bot_type.grid(row=0, column=0, padx=(50,10), pady=(10,8), sticky="")
        self.radio_button_normal = customtkinter.CTkRadioButton(master=self.PROGRESS_frame, text="Normal Çalış", variable=self.radio_var, value=0,command=self.radio_button_web_mode_change)
        self.radio_button_normal.grid(row=1, column=0, padx=(30,10), pady=(0,10), sticky="")
        self.radio_button_hide = customtkinter.CTkRadioButton(master=self.PROGRESS_frame, text="Arka Planda Çalış", variable=self.radio_var, value=1,command=self.radio_button_web_mode_change)
        self.radio_button_hide.grid(row=2, column=0, padx=(57,10), pady=(0,45), sticky="")
        self.combobox_mod = customtkinter.CTkComboBox(self.PROGRESS_frame, values=["Hızlı Mod", "Normal mod"],command=self.combobox_mod_change)
        self.combobox_mod.grid(row=3, column=0, padx=(30,0), pady=(0,25),sticky="")
        self.checkbox_var = tkinter.IntVar(value=0)
        self.checkbox_test_mod = customtkinter.CTkCheckBox(master=self.PROGRESS_frame,text="Test Modu Kullanılsın mı?",checkbox_width=20,checkbox_height=20, font=customtkinter.CTkFont(size=10, weight="bold"),variable=self.checkbox_var,command=self.checkbox_test_change)
        self.checkbox_test_mod.grid(row=4, column=0, pady=(0, 0), padx=(15,0), sticky="sw")

        # File Row=1 Column=3
        self.FILE_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="Dosya",scrollbar_button_color=("white", "#4C616C"))
        self.FILE_frame.grid(row=1,rowspan=2, column=3, padx=(10, 30), pady=(0, 0), sticky="NS")
        self.FILE_frame.grid_columnconfigure(0, weight=1)

        self.file_label = customtkinter.CTkLabel(self.FILE_frame, text="Dosya: Test.txt", font=customtkinter.CTkFont(size=10, weight="bold"))
        self.file_label.grid(row=0, column=0, padx=(0,0), pady=(0, 0))

        self.file_textbox = customtkinter.CTkTextbox(self.FILE_frame, width=200, height=800)
        self.file_textbox.grid(row=1, column=0, padx=(0, 0), pady=(0, 0))

        '''''
        # WARNING Row=2 Column=0
        self.BOT_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="WARNING", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.BOT_frame.grid(row=2, column=0, padx=(30, 0), pady=(0, 0), sticky="")
        self.BOT_frame.grid_columnconfigure(0, weight=1)

        self.label_WARNING_File = customtkinter.CTkLabel(self.BOT_frame, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_File.grid(row=0, column=0,padx=(15,0),pady=(20,10),sticky="")
        self.label_WARNING_File.configure(text="TIME OUT")

        self.label_WARNING_timeout = customtkinter.CTkLabel(self.BOT_frame, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_timeout.grid(row=1, column=0,padx=(15,0),pady=(0,10),sticky="")
        self.label_WARNING_timeout.configure(text="NO FILE")

        self.label_WARNING_login = customtkinter.CTkLabel(self.BOT_frame, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_login.grid(row=2, column=0,padx=(15,0),pady=(0,10),sticky="")
        self.label_WARNING_login.configure(text="NO LOGIN")

        self.label_WARNING_con = customtkinter.CTkLabel(self.BOT_frame, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_con.grid(row=3, column=0,padx=(15,0),pady=(0,0),sticky="")
        self.label_WARNING_con.configure(text="NO NETWORK")
        '''''

        # LOGIN Row=2 Column=1
        self.LOGIN_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="LOGIN", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.LOGIN_frame.grid(row=2, column=1, padx=(65, 30), pady=(0, 0), sticky="")
        self.LOGIN_frame.grid_columnconfigure(0, weight=1) 
        self.label_ID = customtkinter.CTkLabel(self.LOGIN_frame, text="",font=customtkinter.CTkFont(size=20, weight="bold"),fg_color=("white", "#919599"),width=200,corner_radius=8)
        self.label_ID.grid(row=0, column=0,padx=(15,0),pady=(0,15),sticky="")
        self.label_ID.configure(text=f"ID: {self.username}")
        self.label_half = customtkinter.CTkLabel(self.LOGIN_frame, text="Manuel",font=customtkinter.CTkFont(size=15, weight="bold"),text_color="white")
        self.label_half.grid(row=1, column=0, padx=(0,100),pady=(0,10),sticky="")
        self.login_switch = customtkinter.CTkSwitch(master=self.LOGIN_frame,text="Automatic",font=customtkinter.CTkFont(size=15, weight="bold"),text_color="#343A3B", onvalue="on", offvalue="off",command=self.switch_login_change)
        self.login_switch.grid(row=1, column=0, padx=(90,0),pady=(0,10),sticky="")
        self.password_var = customtkinter.StringVar()
        self.password_var.trace_add("write", self.on_entry_change)
        self.password_entry = customtkinter.CTkEntry(self.LOGIN_frame,width=180, state="readonly", show="*", textvariable=self.password_var, placeholder_text="Password")
        self.password_entry.grid(row=2, column=0, padx=(20,0),pady=(0,20))

        #self.password_entry.bind("<KeyRelease>", self.on_entry_change)
        self.login_button = customtkinter.CTkButton(self.LOGIN_frame,text="Hesaba Giriş Yap", command=self.login_btn, state="disabled")
        self.login_button.grid(row=3, column=0, padx=(20,0), pady=(0,35))
        self.checkbox_Login_control = customtkinter.CTkCheckBox(master=self.LOGIN_frame,text="Login?",checkbox_width=20,checkbox_height=20,onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_Login_control.grid(row=4, column=0, padx=(10,5),pady=(0, 0), sticky="sw")
        self.control_button = customtkinter.CTkButton(self.LOGIN_frame,text="Login Kontrol Et", command=self.control_btn, state="disabled",width=20)
        self.control_button.grid(row=4, column=0, padx=(90,0), pady=(0,0))

        # BOT START Row=2 Column=1
        self.BOT_frame = customtkinter.CTkScrollableFrame(self.second_frame, label_text="BOT Başlat", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.BOT_frame.grid(row=2, column=2, padx=(30, 70), pady=(0, 0), sticky="")
        self.BOT_frame.grid_columnconfigure(0, weight=1)

        self.label_Coupons = customtkinter.CTkLabel(self.BOT_frame, text="Kupon Sayısı: None",font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_Coupons.grid(row=0, column=0,padx=(45,0),pady=(20,20),sticky="")
        self.label_Cost = customtkinter.CTkLabel(self.BOT_frame, text="Tutar: None",font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_Cost.grid(row=1, column=0,padx=(45,0),pady=(0,20),sticky="")
        self.start_button = customtkinter.CTkButton(self.BOT_frame,text="Bot Başlat", command=self.bot_start_btn,state="disabled")
        self.start_button.grid(row=2, column=0,padx=(45,0), pady=(0,15), sticky="")

        #yeni
        self.label_bar = customtkinter.CTkLabel(self.BOT_frame, text="None",font=customtkinter.CTkFont(size=12, weight="bold"))
        self.label_bar.grid(row=3, column=0,padx=(30,0),pady=(0,5),sticky="")
        self.progressbar = customtkinter.CTkProgressBar(self.BOT_frame, height=20)
        self.progressbar.grid(row=4, column=0, padx=(20, 0), pady=(0, 0),sticky="")
        # Başlangıç değeri 0
        self.progressbar.set(0)
        #endregion

        #region Create Gecmis Islemler Frame
        # Create Gecmis Islemler Frame
        self.third_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # STEPS Row=1 Column=0
        self.STEPS_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="Adımlar", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=580,width=230)
        self.STEPS_frame_2.grid(row=0, column=0,rowspan=2, padx=(20, 0), pady=(65, 0), sticky="")
        self.STEPS_frame_2.grid_columnconfigure(0, weight=1)
        
        self.checkbox_file_control_2 = customtkinter.CTkCheckBox(master=self.STEPS_frame_2,text="Dosya Seçildi mi?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_file_control_2.grid(row=0, column=0, pady=(40, 30), padx=(0,0), sticky="w")
        self.checkbox_progress_control_2 = customtkinter.CTkCheckBox(master=self.STEPS_frame_2,text="İşlem Yöntemleri!",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_progress_control_2.grid(row=1, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_login_control_2 = customtkinter.CTkCheckBox(master=self.STEPS_frame_2,text="LOGIN Olundu mu?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_login_control_2.grid(row=2, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_logincontrol_control_2 = customtkinter.CTkCheckBox(master=self.STEPS_frame_2,text="LOGIN Kontrol Sağlandı mı?",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_logincontrol_control_2.grid(row=3, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_bot_control_2 = customtkinter.CTkCheckBox(master=self.STEPS_frame_2,text="BOT Başlatıldı!",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_bot_control_2.grid(row=4, column=0, pady=(30, 30), padx=(0,0), sticky="w")
        self.checkbox_finish_control_2 = customtkinter.CTkCheckBox(master=self.STEPS_frame_2,text="Bot İşlemleri Bitti",checkbox_width=20,checkbox_height=20, onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_finish_control_2.grid(row=5, column=0, pady=(30, 25), padx=(0,0), sticky="w")

        self.label_info_2 = customtkinter.CTkLabel(self.STEPS_frame_2, text="Bütün Listeleri Temizleme",font=customtkinter.CTkFont(size=10, weight="bold"))
        self.label_info_2.grid(row=6, column=0,padx=(45,0),pady=(10,0),sticky="")

        self.delete_button_2 = customtkinter.CTkButton(self.STEPS_frame_2,text="Listeleri Sil", command=self.delete_list)
        self.delete_button_2.grid(row=7, column=0,padx=(45,0), pady=(5,0), sticky="")

        # create scrollable radiobutton frame
        self.scrollable_done_radiobutton_frame = ScrollableRadiobuttonFrame(self.third_frame, width=300, height=240, radio_type=0, command=self.radiobutton_frame_event_done, username=self.username, label_text="Tamamlanan Kuponlar")
        self.scrollable_done_radiobutton_frame.grid(row=0, column=1, padx=(10, 0), pady=(70, 30), sticky="")

        # Create "Undone" scrollable radiobutton frame
        self.scrollable_undone_radiobutton_frame = ScrollableRadiobuttonFrame(self.third_frame, width=300, height=240, radio_type=1, command=self.radiobutton_frame_event_undone, username=self.username, label_text="Tamamlanmayan Kuponlar")
        self.scrollable_undone_radiobutton_frame.grid(row=0, column=2, padx=(10, 0), pady=(70, 30), sticky="")

        # File Row=1 Column=3
        self.FILE_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="Dosya",scrollbar_button_color=("white", "#4C616C"), width=230)
        self.FILE_frame_2.grid(row=0, rowspan=2, column=3, padx=(10, 10), pady=(70, 0), sticky="NS")
        self.FILE_frame_2.grid_columnconfigure(0, weight=1)

        self.file_label_2 = customtkinter.CTkLabel(self.FILE_frame_2, text="Dosya: Test.txt", font=customtkinter.CTkFont(size=10, weight="bold"))
        self.file_label_2.grid(row=0, column=0, padx=(0,0), pady=(0, 0))

        self.file_textbox_2 = customtkinter.CTkTextbox(self.FILE_frame_2, width=225, height=800)
        self.file_textbox_2.grid(row=1, column=0, padx=(0, 0), pady=(0, 0))

        '''''
        # PROGRESS Row= Column=
        self.PROGRESS_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="PROGRESS", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.PROGRESS_frame_2.grid(row=0, column=3, padx=(10, 10), pady=(60, 30), sticky="")
        self.PROGRESS_frame_2.grid_columnconfigure(0, weight=1)

        self.radio_var_2 = tkinter.IntVar(value=0)
        self.label_bot_type_2 = customtkinter.CTkLabel(master=self.PROGRESS_frame_2, text="--  SELECT BOT TYPE  --")
        self.label_bot_type_2.grid(row=0, column=0, padx=(50,10), pady=(10,8), sticky="")
        self.radio_button_normal_2 = customtkinter.CTkRadioButton(master=self.PROGRESS_frame_2, text="NORMAL", variable=self.radio_var, value=0,command=self.radio_button_web_mode_change)
        self.radio_button_normal_2.grid(row=1, column=0, padx=(30,10), pady=(0,10), sticky="")
        self.radio_button_hide_2 = customtkinter.CTkRadioButton(master=self.PROGRESS_frame_2, text="HIDE", variable=self.radio_var, value=1,command=self.radio_button_web_mode_change, state="disabled")
        self.radio_button_hide_2.grid(row=2, column=0, padx=(30,10), pady=(0,45), sticky="")
        self.combobox_mod_2 = customtkinter.CTkComboBox(self.PROGRESS_frame_2, values=["FAST", "NORMAL"],command=self.combobox_mod_change)
        self.combobox_mod_2.grid(row=3, column=0, padx=(30,0), pady=(0,25),sticky="")
        self.checkbox_var_2 = tkinter.IntVar(value=0)


        
        # WARNING Row= Column=
        self.BOT_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="WARNING", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.BOT_frame_2.grid(row=1, column=0, padx=(20, 0), pady=(30, 0), sticky="")
        self.BOT_frame_2.grid_columnconfigure(0, weight=1)

        self.label_WARNING_File_2 = customtkinter.CTkLabel(self.BOT_frame_2, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_File_2.grid(row=0, column=0,padx=(15,0),pady=(20,10),sticky="")
        self.label_WARNING_File_2.configure(text="TIME OUT")

        self.label_WARNING_timeout_2 = customtkinter.CTkLabel(self.BOT_frame_2, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_timeout_2.grid(row=1, column=0,padx=(15,0),pady=(0,10),sticky="")
        self.label_WARNING_timeout_2.configure(text="NO FILE")

        self.label_WARNING_login_2 = customtkinter.CTkLabel(self.BOT_frame_2, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_login_2.grid(row=2, column=0,padx=(15,0),pady=(0,10),sticky="")
        self.label_WARNING_login_2.configure(text="NO LOGIN")

        self.label_WARNING_con_2 = customtkinter.CTkLabel(self.BOT_frame_2, text="",font=customtkinter.CTkFont(size=10, weight="bold"),fg_color=("white", "#343A3B"),width=200,corner_radius=8)
        self.label_WARNING_con_2.grid(row=3, column=0,padx=(15,0),pady=(0,0),sticky="")
        self.label_WARNING_con_2.configure(text="NO NETWORK")
        '''''

        # LOGIN Row= Column=
        self.LOGIN_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="LOGIN", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.LOGIN_frame_2.grid(row=1, column=1, padx=(20, 0), pady=(30, 0), sticky="")
        self.LOGIN_frame_2.grid_columnconfigure(0, weight=1) 
        
        self.label_ID_2 = customtkinter.CTkLabel(self.LOGIN_frame_2, text="",font=customtkinter.CTkFont(size=20, weight="bold"),fg_color=("white", "#919599"),width=200,corner_radius=8)
        self.label_ID_2.grid(row=0, column=0,padx=(15,0),pady=(0,15),sticky="")
        self.label_ID_2.configure(text=f"ID: {self.username}")
        self.label_half_2 = customtkinter.CTkLabel(self.LOGIN_frame_2, text="Manuel",font=customtkinter.CTkFont(size=15, weight="bold"),text_color="white")
        self.label_half_2.grid(row=1, column=0, padx=(0,100),pady=(0,10),sticky="")
        self.login_switch_2 = customtkinter.CTkSwitch(master=self.LOGIN_frame_2,text="Automatic",font=customtkinter.CTkFont(size=15, weight="bold"),text_color="#343A3B", onvalue="on", offvalue="off",command=self.switch_login_change_2)
        self.login_switch_2.grid(row=1, column=0, padx=(90,0),pady=(0,10),sticky="")
        self.password_var_2 = customtkinter.StringVar()
        self.password_var_2.trace_add("write", self.on_entry_change_2)
        self.password_entry_2 = customtkinter.CTkEntry(self.LOGIN_frame_2,width=180,state="readonly", show="*" ,textvariable=self.password_var_2,placeholder_text="Password")
        self.password_entry_2.grid(row=2, column=0, padx=(20,0),pady=(0,20))
        #self.password_entry.bind("<KeyRelease>", self.on_entry_change)
        self.login_button_2 = customtkinter.CTkButton(self.LOGIN_frame_2,text="Hesaba Giriş Yap", command=self.login_btn_2, state="disabled")
        self.login_button_2.grid(row=3, column=0, padx=(20,0), pady=(0,35))
        self.checkbox_Login_control_2 = customtkinter.CTkCheckBox(master=self.LOGIN_frame_2,text="Login?",checkbox_width=20,checkbox_height=20,onvalue="on", offvalue="off", font=customtkinter.CTkFont(size=10, weight="bold"),state="disabled")
        self.checkbox_Login_control_2.grid(row=4, column=0, padx=(10,5),pady=(0, 0), sticky="sw")
        self.control_button_2 = customtkinter.CTkButton(self.LOGIN_frame_2,text="Login Kontrol Et", command=self.control_btn, state="disabled",width=20)
        self.control_button_2.grid(row=4, column=0, padx=(90,0), pady=(0,0))

        # BOT START Row= Column=
        self.BOT_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="BOT Başlat", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.BOT_frame_2.grid(row=1, column=2, padx=(20, 10), pady=(30, 0), sticky="")
        self.BOT_frame_2.grid_columnconfigure(0, weight=1)

        self.label_1 = customtkinter.CTkLabel(self.BOT_frame_2, text="Kalan Kupon:",font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_1.grid(row=0, column=0,padx=(45,0),pady=(10,0),sticky="")
        #self.label_2 = customtkinter.CTkLabel(self.BOT_frame_2, text="-",font=customtkinter.CTkFont(size=15, weight="bold"))
        #self.label_2.grid(row=1, column=0,padx=(45,0),pady=(10,0),sticky="")
        #self.label_3 = customtkinter.CTkLabel(self.BOT_frame_2, text="-",font=customtkinter.CTkFont(size=15, weight="bold"))
        #self.label_3.grid(row=2, column=0,padx=(45,0),pady=(10,20),sticky="")
        self.start_button_2 = customtkinter.CTkButton(self.BOT_frame_2,text="Bot Başlat", command=self.bot_start_btn_2, state="disabled")
        self.start_button_2.grid(row=3, column=0,padx=(45,0), pady=(0,20), sticky="")
        #self.checkbox_test_mod_2 = customtkinter.CTkCheckBox(master=self.BOT_frame_2,text="Test Mode?",checkbox_width=20,checkbox_height=20, font=customtkinter.CTkFont(size=10, weight="bold"),variable=self.checkbox_var,command=self.checkbox_test_change)
        #self.checkbox_test_mod_2.grid(row=4, column=0, pady=(15, 0), padx=(15,0), sticky="sw")
        
        '''''
        # UPDATE_DELETE LIST Row= Column=
        self.Delete_frame_2 = customtkinter.CTkScrollableFrame(self.third_frame, label_text="UPDATE & DELETE", orientation="horizontal",scrollbar_button_color=("white", "#4C616C"),height=230,width=230)
        self.Delete_frame_2.grid(row=1, column=3, padx=(10, 10), pady=(30, 0), sticky="")
        self.Delete_frame_2.grid_columnconfigure(0, weight=1)
        
        self.label_info_2 = customtkinter.CTkLabel(self.Delete_frame_2, text="UPDATE All List",font=customtkinter.CTkFont(size=15, weight="bold"))
        self.label_info_2.grid(row=0, column=0,padx=(45,0),pady=(15,0),sticky="")
        
        self.update_button_2 = customtkinter.CTkButton(self.Delete_frame_2,text="LIST UPDATE", command=self.update_list)
        self.update_button_2.grid(row=1, column=0,padx=(45,0), pady=(5,0), sticky="")
        '''''

        # select default frame
        self.select_frame_by_name("home")
        #endregion

    #region Other UI
    def select_frame_by_name(self, name):   
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.frame_2_button.configure(fg_color=("gray75", "gray25") if name == "frame_2" else "transparent")
        self.frame_3_button.configure(fg_color=("gray75", "gray25") if name == "frame_3" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "frame_2":
            self.second_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.second_frame.grid_forget()
        if name == "frame_3":
            self.third_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.third_frame.grid_forget()

        # set default values
        self.scaling_optionemenu.set("100%")
        self.appearance_mode_optionemenu.set("System")

        self.textbox.insert("0.0", "Merhaba Değerli Kullanıcılar,\n\nSizi İddia Bot'unuzun dünyasına hoş geldiniz demeye davet ediyoruz! Bu otomatik işlem botu, bahis ve iddia oyunlarına ilgi duyanlar için geliştirilmiş güçlü bir araçtır. İşte size botumuz hakkında bilgi vermek istiyoruz:\n\nİddia Botu Nedir?\n\nİddia botu, iddia sitelerinde otomatik işlem yapabilen bir yazılımdır. Bu bot, size belirli parametreler ve stratejilere dayalı olarak otomatik bahis yapma yeteneği sunar. Bu, iddia oyunlarında daha fazla kontrol ve etkili yönetim sağlar.\n\nBotumuzun Avantajları:\n\nOtomatik İşlem: Botumuz, kullanıcı tanımladığınız kriterlere uygun bahisler yapabilir. Bu, manuel işlemlerle karşılaştırıldığında daha hızlı ve etkili bir şekilde bahis yapmanıza olanak tanır.\n\nStratejik Esneklik: Botun kullanımı, farklı bahis stratejilerini uygulamanıza ve sonuçları izlemenize imkan verir.\n\nHız ve Kesinlik: Botumuz hızlı ve kesin bir şekilde işlem yapabilir, bu da size daha fazla fırsat sunar.\n\nKullanıcı Sorumluluğu:\n\nBotumuzu kullanırken, lütfen aşağıdaki konuları unutmayın:\n\nSorumluluk: Botumuzun kullanımı, size aittir. Bahislerinizin sonuçlarından ve finansal işlemlerinizden siz sorumlusunuz.\n\nKullanıcı Bilgileri: Botumuz, kullanıcı adı ve parola gibi bilgilere erişebilir. Bu bilgilerin güvenliğini sağlamak sizin sorumluluğunuzdadır.\n\nGüvenlik İhlali: Herhangi bir güvenlik ihlali durumunda, lütfen hemen bizimle iletişime geçin.\n\nSorumluluk Reddi: Botumuzun kullanımı, tüm riskleri ve sonuçları kabul ettiğinizi belirtmeniz anlamına gelir. Botun geliştiricileri herhangi bir kayıp veya sorumluluğu üstlenmez.\n\nBaşlayalım!\n\nŞimdi, İddia Bot'unuzun heyecan verici dünyasına dalma zamanı geldi!\n\nSorularınız veya yardım ihtiyacınız olduğunda, lütfen bizimle iletişime geçmekten çekinmeyin. Size keyifli ve kazançlı bir deneyim sunmak için buradayız!\n\n[Easy Bot SporToto]")
        self.textbox.configure(state='disabled')

        self.textbox2.insert("0.0", "BOT KULLANIMI, GÜVENLİK VE SORUMLULUK\n\nSayın Kullanıcılar,\n\nBotumuzu kullanmadan önce lütfen aşağıdaki konuları anladığınızı ve kabul ettiğinizi bilmeniz önemlidir:\n\nBot Kullanımı İle İlgili Uyarılar:\n\nKanun ve Kurallara Saygı: Botun kullanımı yasadışı veya etik olmayan faaliyetler için kullanılmamalıdır. İddia sitelerinin kullanım şartlarını ve yerel yasaları ihlal etmek, ciddi hukuki sonuçlara yol açabilir.\n\nRisk Faktörleri: Bahis ve iddia oyunları her zaman finansal risk içerir. Botunuzun sonuçları tahminlerle sınırlıdır ve garanti kazanç sağlamaz. Oynadığınız miktarı kaybetmeyi göze almalısınız.\n\nOtomatik İşlem Sınırlamaları: İddia botu, kullanım sıklığını ve miktarını belirleyerek otomatik işlem yapar. Ancak bu tür otomasyon, uzun vadeli kayıpları önlemek için kullanıcı tarafından düzenli olarak kontrol edilmelidir.\n\nGüvenlik ve Sorumluluk:\n\nHesap Güvenliği Sorumluluğu: Botun kullanıcıları olarak, kendi hesap güvenliğinizi sağlama sorumluluğunuz vardır. Kullanıcı adı, şifre ve diğer kimlik bilgilerinizi güvende tutmak sizin sorumluluğunuzdadır.\n\nKimlik Bilgileri Paylaşımı: Kimlik bilgilerinizi kimseyle paylaşmamanız önemlidir. Botunuz veya başka bir kişi veya kurum, bu bilgileri talep etmemelidir. Kimlik bilgilerinizin güvende olduğundan emin olmalısınız.\n\nHesap Erişimi Kontrolü: Botunuzu kullanırken başkalarının erişimine karşı dikkatli olmalısınız. Kullandığınız cihazlar ve tarayıcılar güncel ve güvende olmalıdır.\n\nFinansal Sorumluluk: Botunuzun otomatik işlem yapması finansal risk içerir. Kullandığınız miktarı kaybetmeyi göze almalısınız. Kaybedilen paraların sorumluluğu tamamen kullanıcıya aittir.\n\nKullanıcı Hataları: Botun kullanımında yapılan hatalar ve yanlışlıklar kullanıcı tarafından kontrol edilmelidir. Botun sonuçlarına göre düzeltmeler yapmak kullanıcının sorumluluğundadır.\n\nBağımlılık ve Kontrol: Bahis ve iddia oyunlarının bağımlılık yaratabileceğini unutmayın. Kendinizi kontrol altında tutmak ve oynama sıklığını sınırlamak önemlidir.\n\nBotun kullanıcıları olarak, yukarıdaki konuları anladığınızı ve kabul ettiğinizi beyan edersiniz. Herhangi bir sorumluluk veya kayıptan dolayı botun geliştiricileri veya sağlayıcıları sorumlu tutulamaz. Bu açıklamayı dikkate alarak, botun sorumlu bir şekilde kullanılmasını sağlayınız.\n\nBotun kullanımı ile yukarıdaki şartları ve uyarıları kabul ettiğinizi onaylamış olursunuz.\n\nSağlıklı ve güvenli bir deneyim dileriz.\n\nSaygılarımla,\n[Easy Bot SporToto]")
        self.textbox2.configure(state='disabled')

    def home_button_event(self):
        self.select_frame_by_name("home")

    def frame_2_button_event(self):
        self.select_frame_by_name("frame_2")

    def frame_3_button_event(self):
        self.update_list()
        self.select_frame_by_name("frame_3")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        # Extract the numeric part from the percentage string
        new_scaling_float = int(new_scaling.replace("%", "")) / 100

        # Update the current scaling factor
        self.current_scaling = new_scaling_float

        # Calculate the new window size based on the scaling factor
        new_width = int(self.default_width * new_scaling_float)
        new_height = int(self.default_height * new_scaling_float)

        # Update the window geometry
        self.geometry(f"{new_width}x{new_height}")

        # Update the resizable settings
        if new_scaling_float == 1.2:  # If scaling is 120%
            #self.attributes('-fullscreen', True)
            app.state('zoomed')
            self.resizable(1, 1)  # Allow X and Y dimensions to be changed
            customtkinter.set_widget_scaling(self.current_scaling)
        else:
            app.state('normal')
            #self.attributes('-fullscreen', False)
            #self.iconify()
            #self.deiconify()  # Restore the window
            self.resizable(0, 0)  # X and Y dimensions cannot be changed
            customtkinter.set_widget_scaling(self.current_scaling)

        # You can also call your custom method here if needed
        # customtkinter.set_widget_scaling(new_scaling_float)

        #endregion
#endregion

#region Fernet
    # Fernet Generate Key and Encryption
    def check_key_file(self):
        try:
            # Anahtar dosyasını oku, eğer başarılı olursa dosya var demektir
            with open(self.key_file, "rb") as file:
                return True
        except FileNotFoundError:
            # Dosya bulunamazsa veya başka bir hata oluşursa dosya yok demektir
            return False

    def load_key(self):
            # Anahtarı dosyadan oku
            with open(self.key_file, "rb") as file:
                return file.read()
            
    def get_user_left_date(self):
        try:
            # Dosyanın boyutunu kontrol et
            file_path = self.encrypted_credentials_file
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Dosya boş değilse, okuma işlemini gerçekleştir
                with open(file_path, "rb") as file:
                    encrypted_credentials = file.read()

            else:
                err = "Kayıt bulunamadı."
                self.show_warning_popup(err)
                return None

            # Tarihi çöz ve tarih bilgisini al
            decrypted_credentials = self.cipher_suite.decrypt(encrypted_credentials)
            credentials_list = json.loads(decrypted_credentials.decode())

            # Kullanıcının giriş yaptığı ID'ye sahip olan kullanıcıyı bul
            user_data = next((user for user in credentials_list if user["id"] == self.username), None)

            if user_data:
                return user_data.get("left")
            else:
                print("Kullanıcı bulunamadı.")
                err = "Kullanıcı bulunamadı."
                self.show_warning_popup(err)
                return None

        except (FileNotFoundError, json.JSONDecodeError, Fernet.InvalidToken):
            print("Dosya işlemleri sırasında bir hata oluştu.")
            err = "Dosya işlemleri sırasında bir hata oluştu."
            self.show_warning_popup(err)
            return None
#endregion

#region UI Control   
    def combobox_mod_change(self, *args):
        if self.combobox_mod.get() == "NORMAL":
            self.bot_mode="normal"
        else:
            self.bot_mode="fast" 

    def checkbox_test_change(self, *args):
        if self.checkbox_var.get() == 1:
            print("Test Modu Aktif")
            self.test_mode=True
        else:
            print("Test Modu Pasif")
            self.test_mode=False

    def radio_button_web_mode_change(self, *args):
            # Check if the value of radio_var is 1 (HIDE option)
            if self.radio_var.get() == 1:
                # Set the login_switch to be active
                # Disable interaction with login_switch
                self.web_mode="hide"
                switch_var = customtkinter.StringVar(value="on")
                self.login_switch.configure(state='disabled',variable=switch_var)
                self.switch_login_change()
                print(self.web_mode)
            else:
                # Set the login_switch to be inactive (optional, depending on your needs)
                # Enable interaction with login_switch
                self.web_mode="normal"
                switch_var = customtkinter.StringVar(value="off")
                self.login_switch.configure(state='normal',variable=switch_var)
                self.switch_login_change()
                print(self.web_mode)

    def switch_login_change(self, *args):
        if self.login_switch.get() == "on":
            self.login_mode = "full"
            self.label_half.configure(text_color="#343A3B")
            self.login_switch.configure(text_color="white")
            self.password_var.set("")  # Clear the text
            self.password_entry.configure(state='normal', placeholder_text="Password")
            self.login_button.configure(state='disabled')
        else:
            self.login_mode="half"
            self.label_half.configure(text_color="white")  # Change "color_when_off" to the color you want when switch is off
            self.login_switch.configure(text_color="#343A3B")
            self.password_var.set("")  # Clear the text
            self.password_entry.configure(state='readonly', placeholder_text="Password")
            self.login_button.configure(state='disabled')
            if self.f == True:
                self.login_button.configure(state='normal')
            
    def switch_login_change_2(self, *args):
        if self.login_switch_2.get() == "on":
            self.login_mode = "full"
            self.label_half_2.configure(text_color="#343A3B")
            self.login_switch_2.configure(text_color="white")
            self.password_var_2.set("")  # Clear the text
            self.password_entry_2.configure(state='normal', placeholder_text="Password")
            self.login_button_2.configure(state='disabled')
        else:
            self.login_mode="half"
            self.label_half_2.configure(text_color="white")  # Change "color_when_off" to the color you want when switch is off
            self.login_switch_2.configure(text_color="#343A3B")
            self.password_var_2.set("")  # Clear the text
            self.password_entry_2.configure(state='readonly', placeholder_text="Password")
            self.login_button_2.configure(state='disabled')
            if self.f_2 == True:
                self.login_button_2.configure(state='normal')

    def drag_drop_window(self, *args):
        self.ws = TkinterDnD.Tk()
        self.ws.title('Drag And Drop')
        self.ws.geometry('400x400')
        self.ws.config(bg='#fcb103')

        frame = tk.Frame(self.ws)
        frame.pack()

        label_ID = customtkinter.CTkLabel(frame, text="!!!- Dosya Sürükle -!!!", fg_color=("white", "#919599"), width=400, height=400, corner_radius=8, font=customtkinter.CTkFont(size=30, weight="bold"))
        label_ID.pack()

        label_ID.drop_target_register(DND_FILES)
        label_ID.dnd_bind('<<Drop>>', self.on_drop_file)
        self.ws.mainloop()

    def update_textbox(self, lines):
        self.file_textbox.configure(state='normal')
        self.file_textbox.delete("1.0", "end")

        for line in lines:
            self.file_textbox.insert("end", line + "\n")

        self.file_textbox.configure(state='disabled')

    def update_textbox_2(self, lines):
        self.file_textbox_2.configure(state='normal')
        self.file_textbox_2.delete("1.0", "end")

        for line in lines:
            self.file_textbox_2.insert("end", line + "\n")

        self.file_textbox_2.configure(state='disabled')

    def on_entry_change(self, *args):
        # Burada kullanıcı bir şeyler yazdığında yapılması gereken işlemleri gerçekleştirebilirsiniz
        # Örneğin, yazılan metni almak için:
        #entered_text = self.password_var.get()
        if self.lines != None:
            self.login_button.configure(state='normal')
        #print(f"Entered text: {entered_text}")

    def on_entry_change_2(self, *args):
        # Burada kullanıcı bir şeyler yazdığında yapılması gereken işlemleri gerçekleştirebilirsiniz
        # Örneğin, yazılan metni almak için:
        #entered_text = self.password_var.get()
        self.login_button_2.configure(state='normal')
        #print(f"Entered text: {entered_text}")

    def clear_and_display_results(self,data=None):
        # Görsel arayüze erişim sağla
        self.file_textbox.configure(state='normal')
        self.file_textbox.delete("1.0", "end")

        if data is not None:
            for veri in data:
                self.file_textbox.insert("end", veri + "\n")
                warning_message=veri
                self.show_message_and_log(value=4, message=warning_message, log_level=logging.warning)
            # Sonuçların başarıyla görüntülendiğini bildir
            success_message = "Sonuçlar başarıyla görüntülendi."
            self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)

    def update_radiobutton_frames(self, radio_type_done, radio_type_undone):
            
        # Mevcut radio buttons'ları temizle
        self.scrollable_done_radiobutton_frame.refresh_backup_list(radio_type_done)
        self.scrollable_undone_radiobutton_frame.refresh_backup_list(radio_type_undone)

        '''''

        # Güncel radio button listesini al
            done_backups = self.scrollable_done_radiobutton_frame.get_backups(radio_type_done)
            undone_backups = self.scrollable_undone_radiobutton_frame.get_backups(radio_type_undone)

        # Yeniden oluştur
        for backup in done_backups:
            self.scrollable_done_radiobutton_frame.add_item(backup)

        for backup in undone_backups:
            self.scrollable_undone_radiobutton_frame.add_item(backup)

        '''''

#endregion

#region Button
    def drag_drop_window_btn(self):
        self.drag_drop_window()
        self.checkbox_File_control.configure(state='disabled', variable=customtkinter.StringVar(value="on"))
        self.checkbox_file_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.checkbox_progress_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.login_button.configure(state='normal')

    def select_file_btn(self):    
        self.select_file()

        #yeni
        #self.calculate_percentage(30)
        #self.progress_bar(30)

        #t = threading.Thread(target=self.progress_bar, args=(30,))
        #t.start()   

        self.checkbox_File_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.checkbox_file_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.checkbox_progress_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.login_button.configure(state='normal')
    
    def login_btn(self):    
        if self.test_mode==False:
            # Internetten alınan tarih ve saat bilgisini kullan
            internet_time = self.get_internet_time()

            # left değeri var mı kontrol et
            if self.left and self.left < internet_time:
                err = "Üyelik süreniz dolmuş. Lütfen üyelğinizi uzatın, işlemler yapılmayacak."
                self.show_message_and_log(value=2, message=err, log_level=logging.INFO, is_log=1)
                return  # İşlemleri yapmadan fonksiyondan çık

        if self.web_mode == "normal":
            print("Nomal Mode")
            self.normal_web()
        elif self.web_mode == "hide":
            print("Hide Mode")
            self.hide_web()
        
        self.checkbox_login_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
    
    def login_btn_2(self):
        if self.test_mode==False:
            # Internetten alınan tarih ve saat bilgisini kullan
            internet_time = self.get_internet_time()

            # left değeri var mı kontrol et
            if self.left and self.left < internet_time:
                err = "Üyelik süreniz dolmuş. Lütfen üyelğinizi uzatın, işlemler yapılmayacak."
                self.show_message_and_log(value=2, message=err, log_level=logging.INFO, is_log=1)
                return  # İşlemleri yapmadan fonksiyondan çık

        if self.web_mode == "normal":
            print("Nomal Mode")
            self.normal_web()
        elif self.web_mode == "hide":
            print("Hide Mode")
            self.hide_web()
        
        self.checkbox_login_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.start_button_2.configure(state='normal')
    
    def control_btn(self):
        if not self.control_login():
            error_message = "Lütfen önce başarili bir şekilde giriş yapin Parola yanlış olabilir."
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
            return
        
        if self.f == True:
            self.start_button.configure(state='normal')
            self.checkbox_Login_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
            self.checkbox_logincontrol_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        elif self.f_2 == True:
            self.start_button_2.configure(state='normal')
            self.checkbox_Login_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
            self.checkbox_logincontrol_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))

    def bot_start_btn(self):

        if self.test_mode==False:
            # Internetten alınan tarih ve saat bilgisini kullan
            internet_time = self.get_internet_time()

            # left değeri var mı kontrol et
            if self.left and self.left < internet_time:
                err = "Üyelik süreniz dolmuş. Lütfen üyelğinizi uzatın, işlemler yapılmayacak."
                self.show_message_and_log(value=2, message=err, log_level=logging.INFO, is_log=1)
                return  # İşlemleri yapmadan fonksiyondan çık
        if self.web_mode == "hide":
            success_message = "Bot arka planda başlatılıyor, lütfen işlemlerin bitmesini bekleyin ve program ile etkileşime girmeyin. !!-BOL ŞANSLAR-!!"
            self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)
        else:        
            # Tarayıcı penceresini tekrar maksimize etme (bu adım bazen gerekli olabilir)
            self.driver.maximize_window()

        self.checkbox_finish_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.checkbox_bot_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))

        if self.test_mode==False:
            print("Bot Start")
            self.operation()
        else:
            print("Test Mod Bot Start")
            self.operation()

    def bot_start_btn_2(self):

        if self.test_mode==False:
            # Internetten alınan tarih ve saat bilgisini kullan
            internet_time = self.get_internet_time()

            # left değeri var mı kontrol et
            if self.left and self.left < internet_time:
                err = "Üyelik süreniz dolmuş. Lütfen üyelğinizi uzatın, işlemler yapılmayacak."
                self.show_message_and_log(value=2, message=err, log_level=logging.INFO, is_log=1)
                return  # İşlemleri yapmadan fonksiyondan çık 
        if self.web_mode == "hide":
            success_message = "Bot arka planda başlatılıyor, lütfen işlemlerin bitmesini bekleyin ve program ile etkileşime girmeyin. !!-BOL ŞANSLAR-!!"
            self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)
        else:        
            # Tarayıcı penceresini tekrar maksimize etme (bu adım bazen gerekli olabilir)
            self.driver.maximize_window()
    
        self.checkbox_finish_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))

        selected_value = self.combobox_mod.get()
        if selected_value == "FAST":
            print("Hızlı mod seçildi!")
            mark_method=self.single_group_js_mark_checkbox
        elif selected_value == "NORMAL":
            print("Normal mod seçildi.")
            mark_method=self.single_js_mark_checkbox
        elif selected_value == "v5":
            print("V5 mod seçildi.")
            mark_method=self.single_group_mark_checkbox
        elif selected_value == "v3":
            print("V3 mod seçildi.")
            mark_method=self.single_mark_checkbox
        else:
            mark_method=self.single_group_js_mark_checkbox
            print("Bilinmeyen bir mod seçildi.")

        if self.test_mode==False:
            print("Bot Start")
            self.she(mark_method)
        else:
            print("Test Mod Bot Start")
            self.she(mark_method)

    def delete_list(self):
        print("DELETE LIST")

        # Dosyaların bulunduğu dizindeki tüm dosyaları alın
        backup_files = [f for f in os.listdir(self.backup_file_folder) if os.path.isfile(os.path.join(self.backup_file_folder, f))]
        backup_info_files = [f for f in os.listdir(self.backup_info_folder) if os.path.isfile(os.path.join(self.backup_info_folder, f))]

        # Dosyaları sil
        for file in backup_files:
            file_path = os.path.join(self.backup_file_folder, file)
            os.remove(file_path)

        for file in backup_info_files:
            file_path = os.path.join(self.backup_info_folder, file)
            os.remove(file_path)
        
        print("Dosyalar silindi.")
        

        if not os.path.exists(self.backup_info_folder):
            os.mkdir(self.backup_info_folder)


        self.info_file_path = os.path.join(self.backup_info_folder, "backup_info.json")
        try:
            # JSON dosyasını açın ve mevcut yedekleme bilgilerini yükleyin
            with open(self.info_file_path, "r") as json_file:
                pass
        except FileNotFoundError:
            # Dosya bulunamazsa, yeni bir JSON dosyası oluşturun
            backup_info = []
            with open(self.info_file_path, "w") as new_json_file:
                json.dump(backup_info, new_json_file)

        self.update_radiobutton_frames(0, 1)

    def update_list(self):
        self.update_radiobutton_frames(0, 1) # liste guncellenecek.

#endregion

#region Select File
    #####-Select File-#####
    def select_file(self):
        try:
            self.file_path = tkinter.filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
            if self.file_path:
                with open(self.file_path, 'r') as file:
                    lines = [line.strip() for line in file.readlines() if line.strip()]

            if lines:
                self.lines = lines
                self.update_textbox(lines)
                self.show_message_and_log(value=4, message="Dosya Seçildi. Başarılı.", log_level=logging.INFO, is_log=1)

                txt_var = customtkinter.StringVar(value=self.file_path)
                self.file_label.configure(textvariable=txt_var)
                
                label_var_coupons = customtkinter.StringVar(value=f"Kupon Sayısı: {len(lines)}")
                self.label_Coupons.configure(textvariable=label_var_coupons)

                label_var_cost = customtkinter.StringVar(value=f"Maliyet: {len(lines) * 2}")
                self.label_Cost.configure(textvariable=label_var_cost)
                self.f=True
                #self.show_message_and_log(value=0, message="Dosya Secildi. Basarılı.", log_level=logging.INFO)
        except Exception as e:
            error_message = f"Hata oluştu: Dosya Seçilemedi! {str(e)}"
            self.show_error_and_log(value=0, message=error_message, is_log=0, is_raise=1)
            #self.show_error_and_log(value=0, message="ERROR", is_raise=1)

    def on_drop_file(self, event):
        try:
            self.file_path = event.data
            self.file_path = self.file_path.replace('{', '').replace('}', '')
            print("Düşen Dosya Yolu:", self.file_path)
            if self.file_path:
                self.ws.destroy()

                with open(self.file_path, 'r') as file:
                    lines = [line.strip() for line in file.readlines() if line.strip()]
            if lines:
                self.lines = lines
                self.update_textbox(lines)
                self.show_message_and_log(value=4, message="Dosya Seçildi. Başarılı.", log_level=logging.INFO, is_log=1)              

                txt_var = customtkinter.StringVar(value=self.file_path)
                self.file_label.configure(textvariable=txt_var)

                label_var_coupons = customtkinter.StringVar(value=f"Kupon Sayısı: {len(lines)}")
                self.label_Coupons.configure(textvariable=label_var_coupons)

                label_var_cost = customtkinter.StringVar(value=f"Maliyet: {len(lines) * 2}")
                self.label_Cost.configure(textvariable=label_var_cost)
                self.f=True
        except Exception as e:
            error_message = f"Hata oluştu: Dosya Seçilemedi! {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_log=0, is_raise=1)   

#endregion

#region Web Open
    #####-Web Open-#####        
# Web tarayıcısını başlatma
    def normal_web(self):
        try:         
            if hasattr(self, 'driver') and self.driver:
                # Eğer driver varsa, kapat
                self.driver.quit()

            options = Options()
            #sonradan tarayıcının açık kalmasını sağlıyor
            options.add_experimental_option("detach", True)
            options.add_argument("--incognito")

            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            self.driver.get("https://www.nesine.com/sportoto")
            self.driver.maximize_window()
            
            self.accept_cookies()
            self.login_type()
            
        except Exception as e:
            self.login_button.configure(state='normal')
            # Diğer hataları yakalama ve hata mesajı gösterme
            error_message = f"Bir hata oluştu: {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)

    def hide_web(self):
        try:
            success_message = "Bot arka planda açılmaktadır lütfen işlemlerin bitmesini bekleyin ve program ile etkileşime girmeyin."
            self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)

            if hasattr(self, 'driver') and self.driver:
                # Eğer driver varsa, kapat
                self.driver.quit()

            options = Options()
            options.add_argument("--headless")  # Headless modu etkinleştir
            options.add_argument("--incognito")

            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            self.driver.get("https://www.nesine.com/sportoto")

            self.accept_cookies()
            self.login_type()

            success_message = "Login işlemleri tamamlandı. Bot başlatılabilinir."
            self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)
            
        except Exception as e:
            self.login_button.configure(state='normal')
            # Diğer hataları yakalama ve hata mesajı gösterme
            error_message = f"Bir hata oluştu: {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
#endregion

#region Login
    #####-Login-#####  
    def login_type(self):
        try:
            # Otomatik İD giriliyor
            self.perform_half_login()
            
            if self.login_mode == "half":
                print("Half Login")
                self.show_message_and_log(value=4, message="ID Giris Secildi.", log_level=logging.INFO)
                self.control_button.configure(state='normal')
                self.control_button_2.configure(state='normal')
            elif self.login_mode == "full":
                print("Full Login")
                # Tam giriş yapma işlemi
                self.perform_full_login()
                self.show_message_and_log(value=4, message="ID ve Parola Giris Secildi.", log_level=logging.INFO)
                self.control_btn()
            else:
                # Geçersiz giriş yöntemi seçildiğinde hata mesajı gösterme
                error_message = "Geçersiz giriş yöntemi seçildi. Lütfen geçerli bir giriş yöntemi seçin."
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except Exception as e:
            # Diğer hataları yakalama ve hata mesajı gösterme
            error_message = f"Bir hata oluştu: {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)

    def perform_half_login(self):
        try:
            if self.username:
                # Kullanıcı adı alanını bulup kullanıcı adını girme işlemi
                username_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-test-id='header-username-input'][name='header-username-input']")))
                username_input.send_keys(self.username)
                success_message = f"Kullanıcı adı girişi başarılı. {str(self.username)}"
                self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
            else:
                # Kullanıcı adı eksik veya hatalıysa hata mesajı gösterme
                error_message = "Kullanıcı adı eksik veya hatalı. Lütfen geçerli bir kullanıcı adı girin."
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except TimeoutException as e:
            # Timeout hatası durumunda daha spesifik bir hata mesajı ve işlemleri belirtme
            error_message = f"Zaman aşımı hatası: Kullanıcı adı alanı bulunamadı. {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except WebDriverException as e:
            # WebDriver hatası durumunda daha spesifik bir hata mesajı ve işlemleri belirtme
            error_message = f"WebDriver hatası: Kullanıcı adı girişi yapılamadı. {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)

    def perform_full_login(self):
        try:
            if self.f == True :
                password = self.password_entry.get()
            elif self.f_2 == True :
                password = self.password_entry_2.get()

            if password:
                password_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-test-id='header-password-input'][name='header-password-input']")))
                
                password_input.send_keys(password)
                
                login_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-test-id='header-login-btn'][class='btn c343678ddc765679132f']")))
 
                if login_button:
                    login_button.click()
                    self.show_message_and_log(value=4, message="Parola Girisi Basarili.", log_level=logging.INFO)
                else:
                    # Oturum açma düğmesi bulunamadığında hata mesajı gösterme
                    error_message = "Oturum açma düğmesi bulunamadı."
                    self.show_error_and_log(value=4, message=error_message, is_raise=1)
            else:
                # Parola eksik veya hatalı olduğunda hata mesajı gösterme
                error_message = "Parola eksik veya hatalı. Lütfen geçerli bir parola girin."
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except TimeoutException as e:
            # Timeout hatası durumunda daha spesifik bir hata mesajı ve işlemleri belirtme
            error_message = f"Zaman aşımı hatası: Giriş düğmesi bulunamadı. {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except WebDriverException as e:
            # WebDriver hatası durumunda daha spesifik bir hata mesajı ve işlemleri belirtme
            error_message = f"WebDriver hatası: Giriş yapılamadı. {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)

#endregion

#region CONTROL
    #####-CONTROL-#####
    def control_login(self):
        if hasattr(self, 'driver') and self.driver:       
            self.driver.refresh()
            try:
                wait = WebDriverWait(self.driver, 5)
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span[aria-hidden='true'][data-testid='header-userid']")))

                if self.username in element.text:
                    message = f"Sayın {self.username}, başarılı bir şekilde giriş yaptınız ve İD eşleşti."
                    self.show_message_and_log(value=4, message=message, log_level=logging.INFO)
                    return True
                else:
                    error_message = f"Üzgünüz, {self.username} girişi başarısız oldu veya İD eşleşmedi."
                    self.show_error_and_log(value=4, message=error_message, is_raise=1)
                    return False
            except TimeoutException as e:
                # Zaman aşımı hatası durumunda daha spesifik bir hata mesajı ve işlemleri belirtme
                error_message = f"{self.username} Giriş belirli süre içinde yapılamadı veya sayfa yüklenmedi. {str(e)}"
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
                return False
            except WebDriverException as e:
                # WebDriver hatası durumunda daha spesifik bir hata mesajı ve işlemleri belirtme
                error_message = f"WebDriver hatası: Giriş kontrolü yapılamadı. {str(e)}"
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
                return False

    def control_check(self):    

        if self.test_mode==False:
            # Internetten alınan tarih ve saat bilgisini kullan
            internet_time = self.get_internet_time()

            # left değeri var mı kontrol et
            if self.left and self.left < internet_time:
                err = "Üyleik süreniz dolmuş. Lütfen üyelğinizi uzatın, işlemler yapılmayacak."
                self.show_message_and_log(value=2, message=err, log_level=logging.INFO, is_log=1)
                return  False # İşlemleri yapmadan fonksiyondan çık

        if not hasattr(self, 'driver') and self.driver:
            error_message = "Lütfen önce Web acın"
            self.show_error_and_log(value=2, message=error_message, is_raise=1)
            return False

        if not self.control_login():
            error_message = "Lütfen önce başarili bir şekilde giriş yapin"
            self.show_error_and_log(value=2, message=error_message, is_raise=1)
            return False

        if not hasattr(self, 'lines'):
            error_message = "Lütfen önce bir dosya seçin."
            self.show_error_and_log(value=2, message=error_message, is_raise=1)
            return False
        
        if self.test_mode==False:
            self.start_cost=self.total()
            self.cal_cost=((len(self.lines))*2)
            self.show_message_and_log(value=4, message=self.cal_cost, log_level=logging.INFO)

            if not self.start_cost >= self.cal_cost:
                error_message = "Lütfen önce yeterli bakiye yükleyin hesabınıza."
                self.show_error_and_log(value=2, message=error_message, is_raise=0)
                return False

        # Eğer tüm kontroller başarılı ise True döndür
        success_message = "Kontroller başarılı bir şekilde tamamlandı."
        self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
        return True
    
    def control_process_group(self,current_row_index):
        # ilk para
        total = self.total()

        # Grubun işlemleri tamamlandıktan sonra butonları tıkla
        self.click_buttons(current_row_index)
        
        # İşlemler sonrası toplamı yeniden kontrol et
        total_after_refresh = self.total()

        if self.test_mode==False:
            # Eğer işlemler sonrası toplam, işlemler öncesinden büyükse uyumsuzluk durumunu işle
            if total <= total_after_refresh:
                return self.handle_balance_mismatch(total)
            else:
                return True
        else:
            return True

    #####-#####
#endregion

#region START_PROCESS
    #####-START_PROCESS-#####
    def operation(self):
        if self.control_check():
            if self.test_mode==False:
                self.backup_file()

            self.select_process(is_group_operation=self.is_group_operation, is_multi_option=self.is_multi_option)  


            if self.test_mode==False: 
                if self.miss_data_process() == False:
                     # Döngü normal olarak tamamlandıysa, yani her iki denemede de kontrol başarısız oldu
                    print("Hata: İşlemler başarısız oldu tekrar deneyin veya iletişime geçin.")
                    self.update_radiobutton_frames(0, 1) # liste guncellenecek.
                    return
        else:
            error_message = "Kontrol işlemleri başarısız olduğu için işlem iptal edildi."
            self.start_button.configure(state="disable")
            self.show_error_and_log(value=2, message=error_message, is_raise=1)
            return

        if self.test_mode==False:
            #Update Info
            self.update_backup_info(file_name=None, updated_status="done",row="None",miss="None")

        self.update_radiobutton_frames(0, 1)
        self.checkbox_finish_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        success_message = "...!!-Islemler Tamamlandi ve Basarili-!!..."
        self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)
        self.driver.quit()

    def select_process(self, is_group_operation=True, is_multi_option=False):

        data = self.lines

        group_size = self.group_size if is_group_operation else 1

        selected_value = self.combobox_mod.get()

        if selected_value == "FAST":
            print("Hızlı mod seçildi!")
            mark_method=self.single_group_js_mark_checkbox
        elif selected_value == "NORMAL":
            print("Normal mod seçildi.")
            mark_method=self.single_js_mark_checkbox
        elif selected_value == "v5":
            print("V5 mod seçildi.")
            mark_method=self.single_group_mark_checkbox
        elif selected_value == "v3":
            print("V3 mod seçildi.")
            mark_method=self.single_mark_checkbox
        else:
            mark_method=self.single_group_js_mark_checkbox
            print("Bilinmeyen bir mod seçildi.")

        if self.test_mode==False:
            self.update_backup_info(file_name=None, updated_status="process",row=None,miss=None)


        if not (is_multi_option and is_group_operation):
            self.single_process(mark_method, data, group_size, -1)
        else:
            print("multi")
            #self.multi_process(data, group_size)
    
    def miss_data_process(self): 
        backup_info=self.get_backup_info()
        # Mevcut yedekleme bilgilerini güncelleyin
        for info in backup_info:
        
            if info["file_name"] == self.info_file_name:                
                miss_file_name =info["miss"]

                if miss_file_name != "none":
                    #Update Info
                    self.update_backup_info(file_name=None, updated_status="miss",row=None,miss=None)
                    mark_method=self.single_group_js_mark_checkbox
                    # "miss_" ön ekli dosya yolu oluşturun
                    miss_file_path = os.path.join(self.backup_file_folder, f"{miss_file_name}.txt")

                    with open(miss_file_path, 'r') as miss_file:
                        lines = [line.strip() for line in miss_file.readlines() if line.strip()]
                    
                    for _ in range(self.try_count):
                        if lines:
                            data=lines  

                            # Dosyayı yazma modunda açarak içeriği tamamen sil
                            with open(miss_file_path, "w") as miss_file:
                                pass  # Dosyayı temizledik

                            finish_cost=self.total()
                            if finish_cost > (self.start_cost - self.cal_cost):
                                success_message = "İşlem eksikler var ve kontrol ediliyor."
                                self.show_message_and_log(value=4, message=success_message, log_level=logging.warning)
                                self.driver.refresh()
                                finish_cost=self.total()
                                if abs(finish_cost - (self.start_cost - self.cal_cost)) > 2:
                                    success_message = "Eksik işlemler var ve tekrar elden geçirilecek."
                                    self.show_message_and_log(value=4, message=success_message, log_level=logging.warning)
                                    self.single_process(mark_method, data, group_size=4, starting_row_index=-1)
                                else: break
                            else: break
                            self.clear_and_display_results()
                            # "miss" dosyasını açarak verileri okuyun
                            with open(miss_file_path, 'r') as miss_file:
                                lines = [line.strip() for line in miss_file.readlines() if line.strip()]
                        else:
                            return True
                    else:
                        return False

#yeni
    def progress_bar(self,processed):
        total = (len(self.lines))  # Toplam sayı
        processed = processed + 1  # İşlenen öğe sayısı
        percentage = (processed / total) * 100

        label_bar = customtkinter.StringVar(value=f"İlerleme: % {int(percentage)}")
        self.label_bar.configure(textvariable=label_bar)
        self.progressbar.set(percentage)

    def calculate_percentage(self, processed):
        if True:
            total = len(self.lines)  # Total number
            processed = processed + 1  # Processed item count
            percentage = (processed / total) * 100

            # If cmd.exe process is not running, open a new cmd and print progress
            if self.cmd_process is None or self.cmd_process.poll() is not None:

                command = f'echo Progress: {percentage:.2f}% & pause'
                self.cmd_process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                print(f'New cmd.exe process PID: {self.cmd_process.pid}')

            else:
                print(f'Existing cmd.exe process PID: {self.cmd_process.pid}')

    def terminate_cmd(self):
        if self.cmd_process is not None:
            os.kill(self.cmd_process.pid, signal.SIGTERM)
            print(f'Terminated cmd.exe process PID: {self.cmd_process.pid}')
            self.cmd_process = None
#endregion

#region BACKUP FILE
    #####-BACKUP_FILE-##### self.backup_file()
    def backup_file(self, file_path=None):
        if file_path is None:
            file_path = self.file_path

        if not os.path.exists(self.backup_file_folder):
            os.mkdir(self.backup_file_folder)

        file_name, _ = os.path.splitext(os.path.basename(file_path))
        backup_file_current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_file_name=(f"{file_name}_{backup_file_current_time}")
        backup_file_path = os.path.join(self.backup_file_folder, f"{backup_file_name}.txt")
        shutil.copyfile(file_path, backup_file_path)
        self.save_backup_info(backup_file_name,backup_file_current_time)

    #####-BACKUP_INFO_JSON-#####
    def save_backup_info(self, backup_file_name,backup_file_time):

        self.info_file_name = backup_file_name

        # Yedekleme bilgilerini JSON dosyasına ekleyin
        backup_info = self.get_backup_info()

        backup_info_entry = {
            "file_name": self.info_file_name,
            "backup_time": backup_file_time,
            "status": "process",
            "row": "-1",
            "miss": "none",
            "id" : self.username
        }

        backup_info.append(backup_info_entry)
        # JSON dosyasına güncellenmiş yedekleme bilgilerini kaydedin
        with open(self.info_file_path, "w") as json_file:
            json.dump(backup_info, json_file)

    def miss_coupon_save(self,line_group):

        # "miss_" ön dosya adi oluşturun
        miss_file_name = (f"miss_{self.info_file_name}")
        # "miss_" ön ekli dosya yolu oluşturun
        miss_file_path = os.path.join("backup_file", f"{miss_file_name}.txt")

        # Dosyanın varlığını kontrol edin
        if not os.path.exists(miss_file_path):
            # Dosya yoksa, yeni dosyayı oluşturun ve içeriğini boş bırakabilirsiniz
            with open(miss_file_path, "w") as miss_file:
                pass
                # Update Info
                self.update_backup_info(file_name=None, updated_status=None, row=None, miss=miss_file_name)
                    
        # Verileri dosyanın sonuna eklemek için "append" modunda dosyayı açın
        with open(miss_file_path, "a") as miss_file:
            # Eklemek istediğiniz veriyi yazın (örneğin, line_group)
            miss_file.write("\n".join(line_group)+"\n")
            
    def get_backup_info(self):

        if not os.path.exists(self.backup_info_folder):
            os.mkdir(self.backup_info_folder)

        self.info_file_path = os.path.join(self.backup_info_folder, "backup_info.json")

        try:
            # JSON dosyasını açın ve mevcut yedekleme bilgilerini yükleyin
            with open(self.info_file_path, "r") as json_file:
                backup_info = json.load(json_file)
        except FileNotFoundError:
            # Dosya bulunamazsa, yeni bir JSON dosyası oluşturun
            backup_info = []
            with open(self.info_file_path, "w") as new_json_file:
                json.dump(backup_info, new_json_file)

        return backup_info

    def update_backup_info(self, file_name=None, updated_status=None, row=None, miss=None):
        backup_info = self.get_backup_info()
        if file_name is None:
            file_name = self.info_file_name

        # Mevcut yedekleme bilgilerini güncelleyin
        for info in backup_info:
            if info["file_name"] == file_name:
                if updated_status is not None:
                    info["status"] = updated_status
                if row is not None:
                    info["row"] = row
                if miss is not None:
                    info["miss"] = miss
                # JSON dosyasına güncellenmiş yedekleme bilgilerini kaydedin
                with open(self.info_file_path, "w") as json_file:
                    json.dump(backup_info, json_file)
#endregion

#region PROCESS_METHOD
    #####-SINGLE-#####
    def single_process(self,mark_method, data, group_size=4, starting_row_index=-1):
        group_index = 0
        line_group = []
        control_check=None
        for current_row_index, line in enumerate(data):
            # Skip until the starting row index is reached
            if current_row_index <= starting_row_index:
                continue
            print(f'Row: {current_row_index}')
            print(f"Pattern: {line}")
            line_group.append(line)
            group_index += 1
            if group_index == group_size or current_row_index == (len(data) - 1):
                # Mark checkboxes for the group
                if mark_method(line_group) == True :
                    control_check=self.control_process_group(current_row_index)      
                    # Control and process the group
                    for _ in range(self.try_count):  # İki kez denemek için döngü
                        if control_check==True:
                            break  # Eğer kontrol başarılı ise döngüden çık
                        else:
                            #Update Info
                            self.update_backup_info(file_name=None, updated_status=None,row=(current_row_index - 4),miss=None)
                            self.show_message_and_log(value=4, message="Kupon Onaylama Sayfası Açıldı. Kupon Oynandı. Oyna Butonu Tıklandı.", log_level=logging.INFO)

                            mark_method(line_group)  # Eğer kontrol başarısız ise tekrar işlem yap
                            control_check=self.control_process_group(current_row_index)
                    else:
                        # Döngü normal olarak tamamlandıysa, yani her iki denemede de kontrol başarısız oldu
                        print("Hata: İşlemler başarısız oldu işlenmeyen veriler kayıt edildi.")
                        self.miss_coupon_save(line_group)
                    line_group = []
                    group_index = 0
            current_row_index += 1

    # region MULTI_PROCESS
    #####-MULTI-#####
    def multi_process(self, data, group_size=4):
        """
        Perform payment for a list of data patterns.

        Args:
            data (list): List of data patterns.
            group_size (int, optional): Size of each payment group. Default is 4.
        """
        current_row_index = 0
        line_group = []
        group_index = 0

        for current_row_index, line in enumerate(data):
            print(f'Row: {current_row_index}')
            print(f"Pattern: {line}")

            line_group.append(line)
            group_index += 1

            if group_index == group_size or current_row_index == len(data) - 1:
                # Start parallel processing to mark checkboxes for the group
                self.mark_checkbox_threaded(line_group)
                # Control and process the group
                self.control_process_group(current_row_index)
                line_group = []  # Create a new group
                group_index = 0
            current_row_index += 1
 
    def mark_checkbox_threaded(self, data):
        num_threads = 4
        chunk_size = len(data) // num_threads
        threads = []

        def process_data_chunk(chunk, start_index):
            try:
                for i, line in enumerate(chunk):
                    group_index = start_index + i  # Farklı iş parçacıklarına farklı group_index değerleri ver
                    self.multi_js_mark_checkbox(line, group_index)
            except Exception as e:
                # Hata günlüğüne kaydedin
                error_message =(f"Hata oluştu: {str(e)}")
                self.show_error_and_log(value=0, message=error_message, is_raise=1)

        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size if i < num_threads - 1 else len(data)
            data_chunk = data[start:end]

            thread = threading.Thread(target=process_data_chunk, args=(data_chunk, start))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    #####-#####
    #endregion
#endregion

#region CHECKBOX_MARK_METHOD
    #####-V3_OLD_SİNGLE-#####
    def single_mark_checkbox(self, line_group):
        for group_index, line in enumerate(line_group, group_index=0):
            for row_index, character in enumerate(line, start=1):
                character_column = self.get_character_column(character)
                if character_column is None:
                    # Bilinmeyen karakter için hata mesajı oluştur
                    error_message = f"Bilinmeyen karakter: {character}"
                    self.show_error_and_log(value=0, message=error_message, is_raise=1)
                    return False
                try:
                    checkbox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]')))
                    if self.click_checkbox(checkbox):
                        success_message = "Checkbox işaretli."
                        self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
                    else:
                        error_message = f"Checkbox Bulunamadı"
                        self.show_error_and_log(value=4, message=error_message, is_raise=1)
                except ElementNotInteractableException:
                    error_message = f"CheckBox etkileşimde değil"
                    self.show_error_and_log(value=4, message=error_message, is_raise=1)
        return True

    def multi_mark_checkbox(self, line, group_index):
        for row_index, character in enumerate(line, start=1):
            character_column = self.get_character_column(character)
            if character_column is None:
                # Bilinmeyen karakter için hata mesajı oluştur
                error_message = f"Bilinmeyen karakter: {character}"
                self.show_error_and_log(value=0, message=error_message, is_raise=1)

            with self.group_index_lock:
                try:
                    checkbox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]')))
                    if self.click_checkbox(checkbox):
                        success_message = "Checkbox işaretli."
                        self.show_message_and_log(value=0, message=success_message, log_level=logging.INFO)
                    else:
                        error_message = f"Checkbox Bulunamadı"
                        self.show_error_and_log(value=0, message=error_message, is_raise=1)
                except ElementNotInteractableException:
                    error_message = f"CheckBox etkileşimde değil"
                    self.show_error_and_log(value=0, message=error_message, is_raise=1)
    #####-#####

    #####-V5_OLD_ARRAY-#####
    def single_group_mark_checkbox(self, line_group):
        checkboxs = []
        for group_index, line in enumerate(line_group, group_index=0):
            for row_index, character in enumerate(line, start=1):
                character_column = self.get_character_column(character)
                if character_column is None:
                    # Bilinmeyen karakter için hata mesajı oluştur
                    error_message = f"Bilinmeyen karakter: {character}"
                    self.show_error_and_log(value=4, message=error_message, is_raise=1)
                    return False

                checkbox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]')))
                checkboxs.append(checkbox)
        self.click_checkboxs(checkboxs)
        return True

    def multi_group_mark_checkbox(self, line, group_index):
        checkboxs = []
        for row_index, character in enumerate(line, start=1):
            character_column = self.get_character_column(character)
            if character_column is None:
                # Bilinmeyen karakter için hata mesajı oluştur
                error_message = f"Bilinmeyen karakter: {character}"
                self.show_error_and_log(value=0, message=error_message, is_raise=1)

            with self.group_index_lock:
                checkbox = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f'input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]')))
                checkboxs.append(checkbox)
        self.click_checkboxs(checkboxs)
    #####-#####

    #####-V7_JS_SİNGLE-#####
    def single_js_mark_checkbox(self, line_group):
        for group_index, line in enumerate(line_group, start=0):
            for row_index, character in enumerate(line, start=1):
                character_column = self.get_character_column(character)

                if character_column is None:
                    error_message = f"Bilinmeyen karakter: {character}"
                    self.show_error_and_log(value=0, message=error_message, is_raise=0)
                    return False
                
                else:
                    script = f'''
                        var checkbox = document.querySelector('input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]');
                        if (checkbox) {{
                            checkbox.click();
                            return checkbox.checked;
                        }} else {{
                            return false;
                        }}
                    '''
                    try:
                        result = self.execute_js(script)
                        if not result:
                            error_message = f"Checkbox işaretlenemedi: Grup {group_index}, Satır {row_index}, Karakter {character}"
                            self.show_error_and_log(value=4, message=error_message, is_raise=1)
                            return False

                    except Exception as e:
                        error_message = f"Hata oluştu: {str(e)}"
                        self.show_error_and_log(value=4, message=error_message, is_raise=1)
                        return False
                    
        success_message = f"JavaScript kodu başarıyla çalıştırıldı.Checkbox tıklama başarılı"
        self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
        return True

    def multi_js_mark_checkbox(self, line, group_index):
        for row_index, character in enumerate(line, start=1):
            character_column = self.get_character_column(character)
            if character_column is None:
                # Bilinmeyen karakter için hata mesajı oluştur
                error_message = f"Bilinmeyen karakter: {character}"
                self.show_error_and_log(value=0, message=error_message, is_raise=1)

            with self.group_index_lock:
                script = f'''
                    var checkbox = document.querySelector('input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]');
                    if (checkbox) {{
                        checkbox.click();
                        return checkbox.checked;
                    }} else {{
                        return False;
                    }}
                '''
                return self.execute_js(script)
    #####-#####

    #####-V9_JS_ARRAY-#####
    def single_group_js_mark_checkbox(self, line_group):
        checkbox_scripts = []

        for group_index, line in enumerate(line_group, start=0):
            for row_index, character in enumerate(line, start=1):
                character_column = self.get_character_column(character)
                if character_column is None:
                    # Bilinmeyen karakter için hata mesajı oluştur
                    error_message = f"Bilinmeyen karakter: {character}"
                    self.show_error_and_log(value=4, message=error_message, is_raise=1)
                    return False
                #print(character)
                # JavaScript checkbox tıklama betiğini oluştur
                checkbox_script = f'''
                    var checkbox = document.querySelector('input[type="checkbox"][data-row="{row_index}"][data-column="{character_column}"][data-group="{group_index}"]');
                    if (checkbox) {{
                        checkbox.click();  // Checkbox'ı işaretle
                    }} else {{
                        var errorMessage = "Checkbox bulunamadı: Grup {group_index}, Satır {row_index}, Karakter {character}";
                        console.error(errorMessage);  // Hata mesajını konsola yazdır
                    }}
                '''
                checkbox_scripts.append(checkbox_script)

        combined_script = '\n'.join(checkbox_scripts)

        # Oluşturulan JavaScript betiği çalıştır      
        if self.execute_js(combined_script):
            success_message = f"JavaScript kodu başarıyla çalıştırıldı.Checkbox tıklama başarılı"
            self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
            return True
        else: return False

        """
        try:
            # Oluşturulan JavaScript betiği çalıştır
            result = self.execute_js(combined_script)
            if not result:
                error_message = f"Checkbox işaretlenemedi: Grup {group_index}, Satır {row_index}, Karakter {character}"
                self.show_error_and_log(value=0, message=error_message, is_raise=1)
        except Exception as e:
            error_message = f"Hata oluştu: {str(e)}"
            self.show_error_and_log(value=0, message=error_message, is_raise=1)
        """

    #####-#####
#endregion

#region CLICK
    #region CHECKBOX_MARK
    #####-CHECKBOX_MARK_METHOD-#####
    def click_checkbox(self, checkbox, max_attempts=3):
        # Kodunuzun çalışmasından önce belirli bir süre bekleme
        #time.sleep(0.3)
        # Define the maximum number of attempts to click the checkbox
        attempts = 0

        while attempts < max_attempts:
            try:
                # Checkbox'ı tıkla
                checkbox.click()

                if checkbox.is_selected():
                    success_message = f"Checkbox tıklama başarılı: {str(checkbox)}"
                    self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
                    return True
            except Exception as e:
                # Hata durumunu kaydet ve devam et
                error_message = f"Checkbox tıklama hatası: {str(e)}"
                self.show_error_and_log(value=4, message=error_message, is_raise=0)
                return False

            # Eğer tıklama işlemi başarısız olursa, attempts sayısını artır
            attempts += 1

        # Eğer tüm denemeler başarısız olursa, False döndür
        error_message = "Checkbox tıklama tüm denemelerde başarısız oldu."
        self.show_error_and_log(value=4, message=error_message, is_raise=1)
        return False

    def click_checkboxs(self, checkboxes, max_attempts=3):
        # Kodunuzun çalışmasından önce belirli bir süre bekleme
        time.sleep(0.2)
        attempts = 0

        while attempts < max_attempts:
            try:
                for checkbox in checkboxes:
                    try:
                        if self.click_checkbox(checkbox):
                            success_message = f"Checkbox tıklama başarılı: {str(checkbox)}"
                            self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)
                        else:
                            error_message = "Checkbox bulunamadı."
                            self.show_error_and_log(value=4, message=error_message, is_raise=0)
                    except ElementNotInteractableException:
                        error_message = "Checkbox etkileşimli değil."
                        self.show_error_and_log(value=4, message=error_message, is_raise=0)

                # Eğer tıklama işlemi başarısız olursa, attempts sayısını artır
                attempts += 1

                if all(checkbox.is_selected() for checkbox in checkboxes):
                    # Eğer tüm checkbox'lar işaretlendiyse, işlemi başarıyla sonlandır
                    return True
            except Exception as e:
                # Hata durumunu kaydet ve devam et
                error_message = f"Checkbox tıklama hatası: {str(e)}"
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
                return False

        # Eğer tüm denemeler başarısız olursa, bir hata ile sonlandır
        error_message = "Checkbox tıklama tüm denemelerde başarısız oldu."
        self.show_error_and_log(value=4, message=error_message, is_raise=1)
        return False

    def execute_js(self, script, max_attempts=3):
        # Kodunuzun çalışmasından önce belirli bir süre bekleme
        #time.sleep(0.2)

        attempts = 0
        while attempts < max_attempts:
            try:
                self.driver.execute_script(script)
                return  True # JavaScript kodu başarıyla çalıştı, işlemi sonlandır
            except WebDriverException as e:
                error_message = f"JavaScript kodu çalıştırılırken hata oluştu: {str(e)}"
                self.show_error_and_log(value=4, message=error_message, is_raise=0)
            attempts += 1

        # Belirli bir sayıda deneme sonucunda hata alındı
        error_message = f"JavaScript kodu {max_attempts} defa çalıştırıldı, ancak hala başarısız. İşlem iptal edildi."
        self.show_error_and_log(value=4, message=error_message, is_raise=1)
        return False

    #endregion

    #region CLICK_BUTTONS   
    #####-BUTTONS_AND_FLOW_RESET_COUPON-#####
    def click_buttons(self,current_row_index):
        # Kodunuzun çalışmasından önce belirli bir süre bekleme
        #time.sleep(0.2)
        try:
            # "Hemen Oyna" butonunu bulma işlemi
            btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#btnCalculate[value='Hemen Oyna']")))
            
            # Butonları tıklıyoruz veya hata mesajı veriyoruz
            if btn:
                btn.click()
                self.show_message_and_log(value=4, message="Kupon oluşturuldu.", log_level=logging.INFO)
            else:
                error_message = "Kupon oluşturma butonu (Hemen Oyna) bulunamadı."
                self.show_error_and_log(value=4, message=error_message, is_raise=1)

            # Kodunuzun çalışmasından önce belirli bir süre bekleme
            #time.sleep(0.2)

            # "Oyna" butonunu bulma işlemi
            btn_play = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#btnPlay.btn.btn-confirm.btsmtt')))

            if self.test_mode==False:
                if btn_play:
                    # JavaScript ile tıklama işlemi
                    #self.driver.execute_script("arguments[0].click();", btn_play)

                    #Update Info
                    self.update_backup_info(file_name=None, updated_status=None,row=current_row_index,miss=None)
                    self.show_message_and_log(value=4, message="Kupon Onaylama Sayfası Açıldı. Kupon Oynandı. Oyna Butonu Tıklandı.", log_level=logging.INFO)
                else:
                    error_message = "Oyna butonu bulunamadı."
                    self.show_error_and_log(value=4, message=error_message, is_raise=1)
            else: print("TEST MODE")

            # Kodunuzun çalışmasından önce belirli bir süre bekleme
            #time.sleep(0.2)

            # Sayfayı istenilen URL'ye yönlendiriyoruz
            self.driver.get("https://www.nesine.com/sportoto")

            # Kodunuzun çalışmasından önce belirli bir süre bekleme
            #time.sleep(0.5)
            # İptal bağlantısını bekliyoruz
            trash_btn = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btn.btn-outline.btn-icon[title="İptal"][href*="Sportoto.Trash"]')))

            if trash_btn:
                self.show_message_and_log(value=4, message="Temizleme butonuna tıklanıyor...", log_level=logging.INFO)
                self.driver.execute_script("arguments[0].click();", trash_btn)
            else:
                error_message = "İptal butonu bulunamadı."
                self.show_error_and_log(value=4, message=error_message, is_raise=1)

            # Butonların işlemi tamamladığını kullanıcıya bildir
            message = "Tıklama İşlemleri tamamlandı. Butonlar sırasıyla tıklandı."
            self.show_message_and_log(value=4, message=message, log_level=logging.INFO)

        except Exception as e:
            error_message = f"Hata oluştu: {str(e)}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)

    #####-BUTTONS_ACCEPT_COOKİES-#####
    def accept_cookies(self):
        try:
            # Sayfanın yüklenmesini bekleyin
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "page-content")))
            
            # JavaScript kullanarak kabul düğmesini tıklayın
            self.driver.execute_script("document.getElementById('c-p-bn').click()")
            
            # JavaScript kullanarak modalı kapatma düğmesini tıklayın
            #self.driver.execute_script("document.getElementById('btn-close').click()")

            # "Kapat" düğmesini bulma ve tıklama
            try:
                close_button = self.driver.find_element(By.CLASS_NAME, "btn-close")
                if close_button.is_displayed():  # ya da if close_button.is_enabled():, isteğe bağlı olarak
                    close_button.click()
                    print("Kapat düğmesi bulundu ve tıklandı.")
                else:
                    print("Kapat düğmesi görünür değil veya etkin değil. Devam ediliyor.")
            except NoSuchElementException:
                print("Kapat düğmesi bulunamadı. Devam ediliyor.")
            
            # Başarılı mesajı loglayın
            self.show_message_and_log(value=4, message="Çerezleri kabul edildi.", log_level=logging.INFO)
        except TimeoutException:
            # Zaman aşımı hatası durumunda loglayın ve hata mesajını gösterin
            error_message = "Çerez kabul düğmesi bulunamadı veya sayfa yüklenemedi."
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except WebDriverException as e:
            # WebDriver istisnası durumunda loglayın ve hata mesajını gösterin
            error_message = f"JavaScript kodu çalıştırılırken hata oluştu: {e}"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
    #endregion
#endregion

#region MESSAGE_METHOD
    #####-LOG_FİLE-#####
    def log_setting(self):
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

        today_str = datetime.now().strftime('%m%d%Y')
        
        # Uygulama akışı için logger (DEBUG seviyesinden itibaren tüm mesajları içerir)
        self.app_logger = self.setup_custom_logger('AppLogger', f'{today_str}_app_log.log', log_level=logging.DEBUG, log_format='%(asctime)s [App]: %(message)s')

        # Hatalar için logger (Sadece ERROR seviyesindeki mesajları içerir)
        self.error_logger = self.setup_custom_logger('ErrorLogger', f'{today_str}_error_log.log', log_level=logging.ERROR, log_format='%(asctime)s [Error]: %(message)s')

        # Diğer logger nesnelerini burada oluşturabilirsiniz
        # self.warning_logger = self.setup_custom_logger('WarningLogger', f'{today_str}_warning_log.log', log_level=logging.WARNING, log_format='%(asctime)s [Warning]: %(message)s')

        # Uygulama akışını logla
        self.app_logger.info('Uygulama başlatıldı.')

    def setup_custom_logger(self, logger_name, log_filename, log_level=logging.INFO, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        # Log dosyasının adını belirle
        log_path = os.path.join(self.log_folder, log_filename)

        # Logger'ı oluştur
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)

        # Dosya işleyicisi (handler) ekleyerek dosyaya loglama yapmasını sağla
        handler = logging.FileHandler(log_path, encoding='utf-8')
        
        # Zaman formatını belirle
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        # Logger'a işleyiciyi ekle
        logger.addHandler(handler)

        # Log dosyasının tarihini kontrol et
        check_date = datetime.now() - timedelta(days=14)
        #check_date_str = check_date.strftime('%m%d%Y')

        # Log dosyasının tarihinden eski ise sil
        for old_log_file in os.listdir(self.log_folder):
            if old_log_file.endswith('_app_log.log') or old_log_file.endswith('_error_log.log'):
                file_date_str = old_log_file.split('_')[0]
                file_date = datetime.strptime(file_date_str, '%m%d%Y')
                if file_date < check_date:
                    old_log_path = os.path.join(self.log_folder, old_log_file)
                    os.remove(old_log_path)

        return logger
    #####-#####

    #####-Message_METHOD-#####
    def show_message_and_log(self, value=3, message="INFO", log_level=logging.INFO, is_log=0):
        try:
            if value == 1 or value == 2:
                self.console_message(message, log_level)
                self.show_warning_popup(message)
            elif value == 3 or value == 4:
                self.console_message(message, log_level)
            elif value == 5 or value == 6:
                self.show_warning_popup(message)

            if is_log == 1 or value == 2 or value == 4 or value == 6 or value == 0:
                if log_level == logging.INFO:
                    self.app_logger.info(message)
                elif log_level == logging.WARNING:
                    self.app_logger.warning(message)
                elif log_level == logging.DEBUG:
                    self.app_logger.debug(message)

        except Exception as e:
            error_message = f"Hata oluştu: {str(e)}"
            self.show_error_and_log(value=0, message=error_message, is_log=0, is_raise=1)

    def show_error_and_log(self, value=3, message="ERROR", is_log=0, is_raise=0):
        if value == 1 or value == 2:
            self.console_message(message, logging.ERROR)
            self.show_warning_popup(message)
        elif value == 3 or value == 4:
            self.console_message(message, logging.ERROR)
        elif value == 5 or value == 6 : 
            self.show_warning_popup(message)
        
        if is_log == 1 or value == 2 or value == 4 or value == 6 or value == 0:
            self.error_logger.error(message)
            self.app_logger.error(message)

        if is_raise == 1:
            raise ValueError(message)
        
    #####-#####

    #####-POPUP_MESSAGE-#####
    def show_warning_popup(self, message="ERROR"):
        root = tkinter.Tk()
        root.withdraw()  # Ana pencereyi gizle
        try:
            messagebox.showwarning("Uyarı", message)
        except Exception as e:
            # Hata oluştuğunda logla
            error_message = f"Uyarı penceresi açılırken hata oluştu: {str(e)}"
            self.error_logger.error(error_message)
        finally:
            root.destroy()  # Pencereyi kapat
    #####-#####

    #####-CONSOLE_MESSAGE-#####
    def console_message(self, message="ERROR", log_level=logging.INFO):

        logger = logging.getLogger("App")

        log_prefix = {
            logging.INFO: "[INFO]",
            logging.WARNING: "[WARNING]",
            logging.ERROR: "[ERROR]",
            logging.DEBUG: "[DEBUG]",
        }.get(log_level, "[UNKNOWN]")

        formatted_message = f"{log_prefix}: {message}"
        print(formatted_message)
    #####-#####

    #####-CONSOLE_OPEN_CONTROL-#####
    def open_console_if_not_open(self):
        cmd_check = os.popen('tasklist /FI "IMAGENAME eq cmd.exe"').read()
        if "cmd.exe" not in cmd_check:
            os.system('start cmd')
    #####-#####
#endregion

#region UTILITY
    #####-UTILITY-##### 
    def total(self):
        try:
            # WebDriverWait ile bekleyerek elementi bulun
            wait = WebDriverWait(self.driver, 10)
            span_element = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="d9f05012525436b343bd" and @aria-hidden="true" and @data-testid="header-bakiye"]')))
            total = span_element.text

            # Değişkeni int türüne çevirin
            try:
                total = float(total.replace(" TL", "").replace(",", "").replace(".", "").replace(",", ".")) / 100
                message = "Bakiye (integer): " + str(total)
                self.show_message_and_log(value=4, message=message, log_level=logging.INFO)
                return total
            except ValueError:
                error_message = "Bakiye metni bir tamsayıya çevrilemiyor."
                self.show_error_and_log(value=4, message=error_message, is_raise=1)
        except TimeoutException:
            error_message = "Bakiye elementi belirli süre içinde bulunamadı veya sayfa yüklenmedi."
            self.show_error_and_log(value=4, message=error_message, is_raise=1)

    def handle_balance_mismatch(self, total):

        #time.sleep(0.5)
        # Sayfayı yeniden yükle
        self.driver.refresh()
        total_after_refresh = self.total()

        if total <= total_after_refresh:
            # Bakiyeler eşleşmiyorsa, işlem geçmişini geriye doğru ekleyin
            self.show_message_and_log(value=4, message="Bakiyeler eşleşmiyor", log_level=logging.warning)

            return False
        else:
            return True

    def get_character_column(self, character):
        if character == '1':
            return 0
        elif character in ['x', 'X']:
            return 1
        elif character == '2':
            return 2
        else:
            return None
    
    def get_internet_time(self):
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org')
        
        # NTP'den alınan tarih ve saat bilgisini kullan
        ntp_time = datetime.utcfromtimestamp(response.tx_time)
        return ntp_time
    
    #yeni
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Çıkış yapmak istiyor musunuz ?"):
            # burada kapatma işlemlerini gerçekleştirin
            self.close_All()

    def close_All(self):
        self.destroy()
        self.close_driver()
        self.close_driver_kill()
        self.close_app()

    def close_app(self):
        self.quit()
        #self.destroy()
        #if "login_page.py" in os.popen('tasklist /FI "IMAGENAME eq login_page.py"').read():
            #os.system("taskkill /f /im login_page.py")
        # 'main.exe' işlemi çalışıyorsa, sonlandır
        #if "main_page.py" in os.popen('tasklist /FI "IMAGENAME eq main_page.py"').read():
            #os.system("taskkill /f /im main_page.py")
        #sys.exit()

    def close_driver(self):
        if hasattr(self, 'driver') and self.driver:
            try:
                # Eğer driver varsa ve hala çalışıyorsa, kapat, ilk önce close kullandığımızda sonrasında hata oluyor.
                #self.driver.close() # Sekmeleri kapatır
                self.driver.quit() #driver sonlandırır.
            except Exception as e:
                print(f"An error occurred while closing the driver: {e}")

    def close_driver_kill(self):
        PROCNAME = "chromedriver" # geckodriver or chromedriver or IEDriverServer
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == PROCNAME:
                proc.kill()
    #####-#####
#endregion

#region SHE
    def she(self,mark_method_arg):
        status = None  # Varsayılan değeri None olarak atıyoruz
        mark_method=mark_method_arg
        backup_info = self.get_backup_info()
        backup_file_name=self.radio_name
        file_path = os.path.join(self.backup_file_folder, f"{backup_file_name}.txt")

        if backup_file_name is None: 
            error_message = "Secim Yap"
            self.show_error_and_log(value=2, message=error_message, is_raise=1)
            return   

        if not hasattr(self, 'driver') and self.driver:
            error_message = "Lütfen önce Giris Yapın"
            self.show_error_and_log(value=2, message=error_message, is_raise=1)
            return   
        
        if not self.control_login():
            error_message = "Lütfen önce başarili bir şekilde giriş yapin veya doğru ID ile giris yapin"
            self.show_error_and_log(value=4, message=error_message, is_raise=1)
            return

        success_message = "Kontroller başarılı bir şekilde tamamlandı."
        self.show_message_and_log(value=4, message=success_message, log_level=logging.INFO)

        # Mevcut yedekleme bilgilerini güncelleyin
        for info in backup_info:
            if info["file_name"] == backup_file_name:
                status = info["status"]
                row = info["row"]
                miss_file_name=info["miss"]

        if status == "process":
            if file_path:
                with open(file_path, 'r') as file:
                    lines = [line.strip() for line in file.readlines() if line.strip()]
                self.lines = lines
            else:
                return
            
            self.info_file_name = backup_file_name

            if self.test_mode == False: 
                self.start_cost = self.total()
                self.cal_cost = (2*(len(self.lines) - (row + 1)))
                self.show_message_and_log(value=4, message=self.cal_cost, log_level=logging.INFO)

                if not self.start_cost >= self.cal_cost:
                    error_message = "Lütfen önce yeterli bakiye yükleyin hesabınıza."
                    self.show_error_and_log(value=2, message=error_message, is_raise=1)
                    return

            # Yedek gerekli değil zaten kaldığı yerden devam ederek done olmak istiyor.
            self.single_process(mark_method, self.lines, group_size=4, starting_row_index=int(row))

            # Dev Test Yaparken burayı kendim değiştireceğim Önemli!!! sonsuza kadar dönmesi ayrıca zaten buraya hiç gelemyecek dosya oluşmayacak
            if self.test_mode==False: 
                if self.miss_data_process() == False:
                     # Döngü normal olarak tamamlandıysa, yani her iki denemede de kontrol başarısız oldu
                    print("Hata: İşlemler başarısız oldu tekrar deneyin veya iletişime geçin.")
                    self.update_radiobutton_frames(0, 1) # liste guncellenecek.
                    return
                
                #Update Info
                self.update_backup_info(file_name=None, updated_status="done",row="None",miss="None")

            self.update_radiobutton_frames(0, 1) # Liste guncellendi
            self.checkbox_finish_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
            self.driver.quit()
            success_message = "...!!-Islemler Tamamlandi ve Basarili-!!..."
            self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)           
        elif status == "miss":
            self.info_file_name = backup_file_name

            if self.miss_miss_you(backup_file_name, miss_file_name, mark_method) == True:
                if self.test_mode==False:
                    #Update Info
                    self.update_backup_info(file_name=None, updated_status="done",row="None",miss="None")

                self.checkbox_finish_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
                self.update_radiobutton_frames(0, 1) # Liste guncellenecek
                self.driver.quit()
                success_message = "...!!-Islemler Tamamlandi ve Basarili-!!..."
                self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)
            else: 
                self.update_radiobutton_frames(0, 1) # Liste guncellendi
                # Döngü normal olarak tamamlandıysa, yani her iki denemede de kontrol başarısız oldu
                error_message="Hata: İşlemler başarısız oldu tekrar deneyin veya iletişime geçin."
                self.show_error_and_log(value=2, message=error_message, is_raise=1)
        elif status == "done":      
   
            if file_path:
                with open(file_path, 'r') as file:
                    lines = [line.strip() for line in file.readlines() if line.strip()]
                self.lines = lines
            else:
                return

            if self.test_mode==False: 
                self.start_cost=self.total()
                self.cal_cost=((len(self.lines))*2)
                self.show_message_and_log(value=4, message=self.cal_cost, log_level=logging.INFO)

                if not self.start_cost >= self.cal_cost:
                    error_message = "Lütfen önce yeterli bakiye yükleyin hesabınıza."
                    self.show_error_and_log(value=2, message=error_message, is_raise=1)
                    return  
                
                # Yedek gerekli çünkü aslında bitmiş kupon farklı bir zamanda tekrar oynanıyor.
                self.backup_file(file_path)

            self.single_process(mark_method, self.lines, group_size=4, starting_row_index=-1)

            # Dev Test Yaparken burayı kendim değiştireceğim Önemli!!! sonsuza kadar dönmesi ayrıca zaten buraya hiç gelemyecek dosya oluşmayacak
            if self.test_mode==False: 
                if self.miss_data_process() == False:
                     # Döngü normal olarak tamamlandıysa, yani her iki denemede de kontrol başarısız oldu
                    error_message="Hata: İşlemler başarısız oldu tekrar deneyin veya iletişime geçin."
                    self.show_error_and_log(value=2, message=error_message, is_raise=1)
                    self.update_radiobutton_frames(0, 1) # liste guncellenecek.
                    return
                
                #Update Info
                self.update_backup_info(file_name=None, updated_status="done",row="None",miss="None")

            self.checkbox_finish_control.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
            self.update_radiobutton_frames(0, 1) # Liste guncellenecek
            self.driver.quit()
            success_message = "...!!-Islemler Tamamlandi ve Basarili-!!..."
            self.show_message_and_log(value=2, message=success_message, log_level=logging.INFO)

    def miss_miss_you(self, backup_file_name, miss_file_name, mark_method_arg):

        miss_file_path = os.path.join(self.backup_file_folder, f"{miss_file_name}.txt")

        if miss_file_path != None:
            if self.test_mode==False:
                #Update Info
                self.update_backup_info(file_name=backup_file_name, updated_status="miss",row=None,miss=None)
                                
            mark_method=mark_method_arg
            
            # "miss" dosyasını açarak verileri okuyun
            with open(miss_file_path, 'r') as miss_file:
                lines = [line.strip() for line in miss_file.readlines() if line.strip()]

            if self.test_mode==False: 
                self.start_cost=self.total()
                self.cal_cost=((len(lines))*2)
                self.show_message_and_log(value=4, message=self.cal_cost, log_level=logging.INFO)

                if not self.start_cost >= self.cal_cost:
                    error_message = "Lütfen önce yeterli bakiye yükleyin hesabınıza."
                    self.show_error_and_log(value=2, message=error_message, is_raise=1)
                    return

            for _ in range(self.try_count):
                if lines:
                    data=lines  

                    # Dosyayı yazma modunda açarak içeriği tamamen sil
                    with open(miss_file_path, "w") as miss_file:
                        pass  # Dosyayı temizledik

                    finish_cost=self.total()
                    if finish_cost > (self.start_cost - self.cal_cost):
                        success_message = "İşlem eksikler var ve kontrol ediliyor."
                        self.show_message_and_log(value=4, message=success_message, log_level=logging.warning)
                        self.driver.refresh()
                        finish_cost=self.total()
                        if abs(finish_cost - (self.start_cost - self.cal_cost)) > 2:
                            success_message = "Eksik işlemler var ve tekrar elden geçirilecek."
                            self.show_message_and_log(value=4, message=success_message, log_level=logging.warning)
                            self.single_process(mark_method, data, group_size=4, starting_row_index=-1)
                        else: break
                    else: break
                    self.clear_and_display_results()
                    # "miss" dosyasını açarak verileri okuyun
                    with open(miss_file_path, 'r') as miss_file:
                        lines = [line.strip() for line in miss_file.readlines() if line.strip()]
                else:
                    return True
            else:
                return False

    def radiobutton_frame_event_done(self):
        self.radio_name=self.scrollable_undone_radiobutton_frame.deselect()
        self.radio_name=self.scrollable_done_radiobutton_frame.get_checked_item()

        self.checkbox_file_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.checkbox_progress_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.f_2=True
        self.login_button_2.configure(state='normal')
        
        print(f"radiobutton frame modified: {self.scrollable_done_radiobutton_frame.get_checked_item()}")


        backup_file_name=self.radio_name
        file_path = os.path.join(self.backup_file_folder, f"{backup_file_name}.txt")

        if file_path:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

        if lines:
            self.update_textbox_2(lines)
            self.show_message_and_log(value=4, message="Dosya Seçildi. Başarılı.", log_level=logging.INFO, is_log=1)

            txt_var = customtkinter.StringVar(value=backup_file_name)
            self.file_label_2.configure(textvariable=txt_var)

    def radiobutton_frame_event_undone(self):
        self.radio_name=self.scrollable_done_radiobutton_frame.deselect()
        self.radio_name=self.scrollable_undone_radiobutton_frame.get_checked_item()

        self.checkbox_file_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.checkbox_progress_control_2.configure(state='disabled',variable=customtkinter.StringVar(value="on"))
        self.f_2=True
        self.login_button_2.configure(state='normal')

        print(f"radiobutton frame modified: {self.scrollable_undone_radiobutton_frame.get_checked_item()}")

        backup_file_name=self.radio_name
        file_path = os.path.join(self.backup_file_folder, f"{backup_file_name}.txt")

        if file_path:
            with open(file_path, 'r') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

        if lines:
            self.update_textbox_2(lines)
            self.show_message_and_log(value=4, message="Dosya Seçildi. Başarılı.", log_level=logging.INFO, is_log=1)

            txt_var = customtkinter.StringVar(value=backup_file_name)
            self.file_label_2.configure(textvariable=txt_var)

        #yeni
            status = None
            backup_info = self.get_backup_info()

            for info in backup_info:
                if info["file_name"] == backup_file_name:
                    status = info["status"]
                    row = info["row"]
                    miss_file_name=info["miss"]
            
            if status == "process": 
                txt_var = customtkinter.StringVar(value=f"Kalan Kupon: {(len(lines)-row)}")
                self.label_1.configure(textvariable=txt_var)
            elif status == "miss":
                miss_file_path = os.path.join(self.backup_file_folder, f"{miss_file_name}.txt")
                with open(miss_file_path, 'r') as miss_file:
                    lines2 = [line.strip() for line in miss_file.readlines() if line.strip()]
                txt_var = customtkinter.StringVar(value=f"Kalan Kupon: {(len(lines)-len(lines2))}")
                self.label_1.configure(textvariable=txt_var)

#endregion

if __name__ == "__main__":
    app = MainPage()
    app.mainloop()
