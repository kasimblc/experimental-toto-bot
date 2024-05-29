import customtkinter
from tkinter import messagebox
from PIL import Image
import os
import json
from cryptography.fernet import Fernet
import subprocess
import sys
import tkinter
from datetime import datetime
import time

class LoginPage(customtkinter.CTk):
    width = 900
    height = 600
    customtkinter.set_appearance_mode("system")

    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.title("Easy Bot SporToto")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.left_date = datetime(2024, 12, 31)  # YYYY, MM, DD formatında son kullanma tarihi

        self.key_file = "fernet_key.key"
        self.encrypted_credentials_file = "encrypted_credentials.json"
        self.user_info_file = "user_info.json"

        # Anahtar dosyasını kontrol et
        if not self.check_key_file():
            # Anahtar dosyası yoksa yeni bir anahtar oluştur
            self.create_key()

        # Anahtarı dosyadan oku
        self.key = self.load_key()
        self.cipher_suite = Fernet(self.key)

        # load and create background image
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open(current_path + "/test_images/bg_gradient.jpg"),
                                               size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)

        # create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_frame.grid(row=0, column=0, sticky="ns")
        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Easy Bot SporToto\n\n\nLogin Page",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.login_label.grid(row=0, column=0, padx=30, pady=(150, 15))
        self.id_entry = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text="ID")
        self.id_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.remember_me()
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=200, show="*", placeholder_text="PASSWORD")
        self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login_btn, width=200)
        self.login_button.grid(row=3, column=0, padx=30, pady=(15, 0))
        self.checkbox_var = tkinter.IntVar(value=0)
        self.checkbox_file_control = customtkinter.CTkCheckBox(master=self.login_frame,text="Beni Hatırla?",checkbox_width=20,checkbox_height=20, variable=self.checkbox_var, font=customtkinter.CTkFont(size=10, weight="bold"))
        # Checkbox'ı başlangıçta işaretli olarak başlatın
        self.checkbox_file_control.select()
        self.checkbox_file_control.grid(row=4, column=0, pady=(0, 100), padx=(170,0), sticky="")
        
        self.create_account_button = customtkinter.CTkButton(self.login_frame, text="Kayıt Oluştur", command=self.open_account_frame, width=200)
        self.create_account_button.grid(row=4, column=0, padx=30, pady=(120, 15))
    
        # Enter tuşuna basıldığında çağrılacak fonksiyonu belirtin
        self.bind("<Return>", self.on_enter_pressed)

        # create account frame
        self.account_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.account_frame.grid_columnconfigure(0, weight=1)
        self.account_label = customtkinter.CTkLabel(self.account_frame, text="Create Account",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.account_label.grid(row=0, column=0, padx=30, pady=(30, 15))

        self.id_create = customtkinter.CTkEntry(self.account_frame, width=200, placeholder_text="Neseine.com ID")
        self.id_create.grid(row=1, column=0, padx=30, pady=(15, 15))

        self.name_create = customtkinter.CTkEntry(self.account_frame, width=200, placeholder_text="name")
        self.name_create.grid(row=2, column=0, padx=30, pady=(15, 15))

        self.mail_create = customtkinter.CTkEntry(self.account_frame, width=200, placeholder_text="@mail")
        self.mail_create.grid(row=3, column=0, padx=30, pady=(15, 15))
        
        self.password_create = customtkinter.CTkEntry(self.account_frame, width=200, show="*", placeholder_text="password")
        self.password_create.grid(row=4, column=0, padx=30, pady=(0, 15))

        self.password_create2 = customtkinter.CTkEntry(self.account_frame, width=200, show="*", placeholder_text="password tekrar")
        self.password_create2.grid(row=5, column=0, padx=30, pady=(0, 15))

        self.create_button = customtkinter.CTkButton(self.account_frame, text="Kayıt OL", command=self.account_create_btn, width=200)
        self.create_button.grid(row=6, column=0, padx=30, pady=(15, 15))

        self.back_button = customtkinter.CTkButton(self.account_frame, text="Back", command=self.close_account_frame, width=200)
        self.back_button.grid(row=7, column=0, padx=30, pady=(30, 15))
          
    #-#Fonksiyonlar#-#

    # Butons
    def account_create_btn(self):
        if not self.id_create.get().isdigit() :
            err = "ID sayısal veri olmalı."
            self.show_warning_popup(err)

        if (self.name_create.get() and
            self.mail_create.get() and
            self.password_create.get() and
            self.password_create.get() == self.password_create2.get()):
            # Yukarıdaki koşulların hepsi sağlandığında işlemleri gerçekleştir
            self.save_login_credentials(
                self.id_create.get(),
                self.name_create.get(),
                self.mail_create.get(),
                self.password_create.get()
            )
            self.account_frame.grid_forget()  # create_account frame'ini kaldır
            self.login_frame.grid(row=0, column=0, sticky="ns")  # login frame'ini göster
        else:
            # Herhangi bir alan boşsa veya şifreler uyuşmuyorsa bir hata mesajı göster veya başka bir işlem yap
            # Örneğin:
            err = "Lütfen tüm alanları doldurun ve şifreleri doğrulayın."
            self.show_warning_popup(err)
            
    def login_btn(self):
        pass_info = self.get_login_credentials()

        if pass_info[0]:  # Giriş başarılı mı?

            id = pass_info[1]

            if self.checkbox_var.get() == 1:
                # Eğer "Beni Hatırla" işaretli ise, kullanıcı bilgilerini kaydet
                self.save_user_info(str(id), "on")
            else:
                # "Beni Hatırla" işareti işaretli değilse, kullanıcı bilgilerini kaydetme
                self.save_user_info("Nesine ID", "off")

            # Burada giriş kontrolü yapabilirsin, başarılıysa ana sayfayı aç
            #process = subprocess.Popen(['main.exe', str(id)])  
            process = subprocess.Popen(['python', 'main_page.py', str(id)])

            # main.exe işi tamamlandıktan sonra
            time.sleep(2)
            #process.wait()

            #app.destroy()
            # login.exe'nin kendi işlemini sonlandır
            #os.system("taskkill /f /im EasyBot.exe")

            # Mevcut pencereyi gizle (unmap)
            sys.exit()
    
    def open_account_frame(self):
        self.login_frame.grid_forget()  # remove login frame
        self.account_frame.grid(row=0, column=0, sticky="nsew", padx=100)  # show create_account frame

    def close_account_frame(self):
        self.account_frame.grid_forget()  # remove create_account frame
        self.login_frame.grid(row=0, column=0, sticky="ns")  # show login frame

    # Login Credentials
    def save_login_credentials(self, id, name, mail, password):
        # Dosyada aynı ID'nin olup olmadığını kontrol et
        existing_records = []

        if os.path.exists(self.encrypted_credentials_file):
            with open(self.encrypted_credentials_file, "rb") as file:
                existing_credentials = file.read()
                if existing_credentials:
                    decrypted_credentials = self.cipher_suite.decrypt(existing_credentials)
                    existing_records = json.loads(decrypted_credentials.decode())

        # Check if the ID already exists
        if any(record["id"] == id for record in existing_records):
            err = f"Bu ID zaten kayıtlı: {id}"
            self.show_warning_popup(err)
            return  # ID zaten varsa işlemi durdur

        # Kullanıcı bilgilerini şifrele
        new_record = {
            "id": id,
            "name": name,
            "mail": mail,
            "password": password,
            "left": str(self.left_date)
        }

        # Add the new record to the existing records
        existing_records.append(new_record)

        # Şifrelenmiş bilgileri dosyaya ekle
        with open(self.encrypted_credentials_file, "wb") as file:
            encrypted_credentials = self.cipher_suite.encrypt(json.dumps(existing_records).encode())
            file.write(encrypted_credentials)

        err = f"Kayıt Yapıldı: {id}"
        self.show_warning_popup(err)

    def get_login_credentials(self):
        username = self.id_entry.get()
        password = self.password_entry.get()

        try:
            # Dosyanın boyutunu kontrol et
            file_path = self.encrypted_credentials_file
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # Dosya boş değilse, okuma işlemini gerçekleştir
                with open(file_path, "rb") as file:
                    encrypted_credentials = file.read()

                # Şifreyi çöz ve bilgileri al
                decrypted_credentials = self.cipher_suite.decrypt(encrypted_credentials)
                credentials_list = json.loads(decrypted_credentials.decode())

                # Tüm kullanıcıları kontrol et
                for user_data in credentials_list:
                    if user_data.get("id") == username and user_data.get("password") == password:
                        print("Giriş yapıldı. Kullanıcı ID:", username)

                        # Diğer giriş başarılı olduğunda yapılacak işlemler buraya gelecek
                        return True, user_data.get("id")

                # Kullanıcı bulunamadıysa
                print("Giriş başarısız. Kullanıcı adı veya şifre hatalı.")
                err = "Giriş başarısız. Kullanıcı adı veya şifre hatalı."
                self.show_warning_popup(err)
                # Diğer giriş başarısız olduğunda yapılacak işlemler buraya gelecek
                return False

            else:
                err = "Kayıt bulunamadı."
                self.show_warning_popup(err)
                # Diğer kayıt bulunamadığında yapılacak işlemler buraya gelecek
                return False

        except (FileNotFoundError, json.JSONDecodeError, Fernet.InvalidToken):
            print("Dosya işlemleri sırasında bir hata oluştu.")
            err = "Dosya işlemleri sırasında bir hata oluştu."
            self.show_warning_popup(err)
            return False

    # Fernet Generate Key and Encryption
    def check_key_file(self):
        try:
            # Anahtar dosyasını oku, eğer başarılı olursa dosya var demektir
            with open(self.key_file, "rb") as file:
                return True
        except FileNotFoundError:
            # Dosya bulunamazsa veya başka bir hata oluşursa dosya yok demektir
            return False

    def create_key(self):
        # Yeni bir anahtar oluştur
        key = Fernet.generate_key()

        # Anahtarı dosyaya yaz
        with open(self.key_file, "wb") as file:
            file.write(key)

    def load_key(self):
        # Anahtarı dosyadan oku
        with open(self.key_file, "rb") as file:
            return file.read()

    # Remember ME
    def save_user_info(self, username, remember_me):
        user_info = {"username": username, "remember_me": remember_me}
        with open(self.user_info_file, "w") as file:
            json.dump(user_info, file)

    def load_user_info(self):
        try:
            with open(self.user_info_file, "r") as file:
                user_info = json.load(file)
                return user_info["username"], user_info["remember_me"]
        except FileNotFoundError:
            return None, None

    def remember_me(self):
        # Program başlatıldığında kullanıcı bilgilerini yükle
        username, remember_me = self.load_user_info()
        # Eğer bilgiler varsa ve "Beni Hatırla" işaretliyse, giriş alanlarını otomatik olarak doldur
        if username and remember_me == "on":
            self.id_entry.insert(0, username)

    # Other
    def on_enter_pressed(self, event):
        # Enter tuşuna basıldığında yapılacak işlemleri burada tanımlayabilirsiniz.
        self.login_btn()

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

if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
