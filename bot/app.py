import subprocess
import sys

# login_page.py'yi başlat
subprocess.Popen(['python', 'login_page.py'])

# Mevcut pencereyi kapat (unmap)
sys.exit()

'''''
    # main_page.exe'yi başlat
    subprocess.run(['main_page.exe', str(id), str(left)], check=True)

    main_page_obj = main_page(id=str(id), left=str(left))
    main_page_obj.mainloop()
    login_page_obj = login_page()
    login_page_obj.mainloop()

    
    # Burada giriş kontrolü yapabilirsin, başarılıysa ana sayfayı aç
    subprocess.Popen(['python', 'main_page.py', str(id), str(left)])

    # Mevcut pencereyi gizle (unmap)
    sys.exit()
'''''