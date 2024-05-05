import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QMessageBox, QDateTimeEdit, QTimeEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
import sqlite3

class Veritabani:
    def __init__(self, dosya):
        self.dosya = dosya
        self.baglanti = sqlite3.connect(dosya)
        self.cursor = self.baglanti.cursor()

    def tablo_olustur(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS hastalar (
                                isim TEXT,
                                tc TEXT PRIMARY KEY
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS doktorlar (
                                isim TEXT PRIMARY KEY,
                                uzmanlik_alani TEXT
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS randevular (
                                tarih TEXT,
                                saat TEXT,
                                doktor TEXT,
                                hasta_tc TEXT,
                                FOREIGN KEY (doktor) REFERENCES doktorlar(isim),
                                FOREIGN KEY (hasta_tc) REFERENCES hastalar(tc)
                                )''')
        self.baglanti.commit()

    def hasta_ekle(self, isim, tc):
        self.cursor.execute("INSERT INTO hastalar VALUES (?, ?)", (isim, tc))
        self.baglanti.commit()

    def doktor_ekle(self, isim, uzmanlik_alani):
        self.cursor.execute("INSERT INTO doktorlar VALUES (?, ?)", (isim, uzmanlik_alani))
        self.baglanti.commit()

    def randevu_al(self, tarih, saat, doktor, hasta_tc):
        self.cursor.execute("INSERT INTO randevular VALUES (?, ?, ?, ?)", (tarih, saat, doktor, hasta_tc))
        self.baglanti.commit()

    def randevu_iptal(self, hasta_tc):
        self.cursor.execute("DELETE FROM randevular WHERE hasta_tc=?", (hasta_tc,))
        self.baglanti.commit()

class Hasta:
    def __init__(self, isim, tc):
        self.isim = isim
        self.tc = tc
        self.randevu_gecmisi = []

class Doktor:
    def __init__(self, isim, uzmanlik_alani):
        self.isim = isim
        self.uzmanlik_alani = uzmanlik_alani
        self.musaitlik_durumu = True

class Randevu:
    def __init__(self, randevu_tarihi, saat, doktor, hasta):
        self.randevu_tarihi = randevu_tarihi
        self.saat = saat
        self.doktor = doktor
        self.hasta = hasta

class RandevuSistemi(QWidget):
    def __init__(self):
        super().__init__()
        self.veritabani = Veritabani("randevu_veritabani.db")
        self.veritabani.tablo_olustur()
        self.setWindowTitle("Hastane Randevu Sistemi")
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        self.background_image = QLabel(self)
        pixmap = self.load_image_from_url("https://www.cumhuriyet.com.tr/Archive/2022/6/9/1945447/kapak_175352.jpg")
        if pixmap:
            pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio)
            self.background_image.setPixmap(pixmap)
            self.background_image.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(self.background_image)

        self.setLayout(main_layout)

        hasta_ekle_groupbox = self.create_hasta_ekle_groupbox()
        doktor_ekle_groupbox = self.create_doktor_ekle_groupbox()
        randevu_al_groupbox = self.create_randevu_al_groupbox()
        randevu_iptal_groupbox = self.create_randevu_iptal_groupbox()

        main_layout.addWidget(hasta_ekle_groupbox)
        main_layout.addWidget(doktor_ekle_groupbox)
        main_layout.addWidget(randevu_al_groupbox)
        main_layout.addWidget(randevu_iptal_groupbox)

        self.exit_button = QPushButton("Çıkış", self)
        self.exit_button.clicked.connect(self.close)
        main_layout.addWidget(self.exit_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

        self.resize(400, 300)
        self.center()

    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().screenGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def create_hasta_ekle_groupbox(self):
        groupbox = QWidget()
        layout = QVBoxLayout()
        groupbox.setLayout(layout)

        self.hasta_isim_entry = QLineEdit()
        layout.addWidget(QLabel("Hasta İsim:"))
        layout.addWidget(self.hasta_isim_entry)

        self.hasta_tc_entry = QLineEdit()
        layout.addWidget(QLabel("TC Kimlik No:"))
        layout.addWidget(self.hasta_tc_entry)

        hasta_ekle_button = QPushButton("Hasta Ekle")
        hasta_ekle_button.clicked.connect(self.hasta_ekle)
        layout.addWidget(hasta_ekle_button)

        return groupbox

    def create_doktor_ekle_groupbox(self):
        groupbox = QWidget()
        layout = QVBoxLayout()
        groupbox.setLayout(layout)

        self.doktor_isim_entry = QLineEdit()
        layout.addWidget(QLabel("Doktor İsim:"))
        layout.addWidget(self.doktor_isim_entry)

        self.doktor_uzmanlik_entry = QLineEdit()
        layout.addWidget(QLabel("Uzmanlık Alanı:"))
        layout.addWidget(self.doktor_uzmanlik_entry)

        doktor_ekle_button = QPushButton("Doktor Ekle")
        doktor_ekle_button.clicked.connect(self.doktor_ekle)
        layout.addWidget(doktor_ekle_button)

        return groupbox

    def create_randevu_al_groupbox(self):
        groupbox = QWidget()
        layout = QVBoxLayout()
        groupbox.setLayout(layout)

        self.randevu_tarih_entry = QDateTimeEdit()
        self.randevu_tarih_entry.setDisplayFormat("yyyy-MM-dd")
        self.randevu_tarih_entry.setCalendarPopup(True)
        layout.addWidget(QLabel("Randevu Tarihi:"))
        layout.addWidget(self.randevu_tarih_entry)

        self.randevu_saat_entry = QTimeEdit()
        layout.addWidget(QLabel("Randevu Saati:"))
        layout.addWidget(self.randevu_saat_entry)

        self.randevu_doktor_entry = QLineEdit()
        layout.addWidget(QLabel("Doktor İsim:"))
        layout.addWidget(self.randevu_doktor_entry)

        randevu_al_button = QPushButton("Randevu Al")
        randevu_al_button.clicked.connect(self.randevu_al)
        layout.addWidget(randevu_al_button)

        return groupbox

    def create_randevu_iptal_groupbox(self):
        groupbox = QWidget()
        layout = QVBoxLayout()
        groupbox.setLayout(layout)

        self.iptal_tc_entry = QLineEdit()
        layout.addWidget(QLabel("Hasta TC:"))
        layout.addWidget(self.iptal_tc_entry)

        iptal_button = QPushButton("Randevu İptal")
        iptal_button.clicked.connect(self.randevu_iptal)
        layout.addWidget(iptal_button)

        return groupbox

    def hasta_ekle(self):
        isim = self.hasta_isim_entry.text()
        tc = self.hasta_tc_entry.text()
        self.veritabani.hasta_ekle(isim, tc)
        QMessageBox.information(self, "Başarılı", f"{isim} hasta başarıyla eklendi.")

    def doktor_ekle(self):
        isim = self.doktor_isim_entry.text()
        uzmanlik_alani = self.doktor_uzmanlik_entry.text()
        self.veritabani.doktor_ekle(isim, uzmanlik_alani)
        QMessageBox.information(self, "Başarılı", f"{isim} doktor başarıyla eklendi.")

    def randevu_al(self):
        tarih = self.randevu_tarih_entry.date().toString(Qt.ISODate)
        saat = self.randevu_saat_entry.time().toString(Qt.ISODate)
        doktor_isim = self.randevu_doktor_entry.text()
        self.veritabani.randevu_al(tarih, saat, doktor_isim, self.hasta_tc_entry.text())
        QMessageBox.information(self, "Başarılı", "Randevu başarıyla oluşturuldu.")

    def randevu_iptal(self):
        hasta_tc = self.iptal_tc_entry.text()
        self.veritabani.randevu_iptal(hasta_tc)
        QMessageBox.information(self, "Başarılı", "Randevu başarıyla iptal edildi.")

    def load_image_from_url(self, url):
        try:
            response = requests.get(url)
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            return pixmap
        except Exception as e:
            print("Arka plan resmi yüklenirken bir hata oluştu:", e)
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    randevu_sistemi = RandevuSistemi()
    randevu_sistemi.show()
    sys.exit(app.exec_())
