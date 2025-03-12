import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QComboBox, QTextEdit, QFrame, QMessageBox, QProgressBar,
                            QCheckBox, QSlider, QGroupBox)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import cv2
import numpy as np
import pytesseract
from PIL import Image

class OcrThread(QThread):
    result_ready = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    
    def __init__(self, image_path, lang, use_preprocessing=True, brightness=0, contrast=0):
        super().__init__()
        self.image_path = image_path
        self.lang = lang
        self.use_preprocessing = use_preprocessing
        self.brightness = brightness
        self.contrast = contrast
        
    def run(self):
        try:
            self.progress_update.emit(10)
            
            # Lecture directe avec PIL pour compatibilité Tesseract
            pil_img = Image.open(self.image_path)
            self.progress_update.emit(30)
            
            # Prétraitement optionnel
            if self.use_preprocessing:
                # Conversion en numpy array pour OpenCV
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
                # Appliquer les ajustements de luminosité et contraste
                if self.brightness != 0 or self.contrast != 0:
                    img = cv2.convertScaleAbs(img, alpha=(self.contrast/50.0)+1, beta=self.brightness)
                
                # Conversion en niveaux de gris
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Seuillage adaptatif pour améliorer le contraste
                thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
                
                # Réduction du bruit
                kernel = np.ones((1, 1), np.uint8)
                processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                
                # Reconversion en image PIL pour Tesseract
                pil_processed = Image.fromarray(processed)
                self.progress_update.emit(60)
                
                # Extraction avec l'image prétraitée
                text = pytesseract.image_to_string(pil_processed, lang=self.lang)
            else:
                # Extraction directe sans prétraitement
                text = pytesseract.image_to_string(pil_img, lang=self.lang)
            
            self.progress_update.emit(90)
            
            # Si le texte est vide, essayer avec d'autres configurations
            if not text.strip():
                # Essayer PSM 6 (block de texte unique)
                text = pytesseract.image_to_string(
                    pil_img, 
                    lang=self.lang,
                    config='--psm 6'
                )
            
            # Si toujours vide, essayer avec PSM 3 (détection automatique complète)
            if not text.strip():
                text = pytesseract.image_to_string(
                    pil_img, 
                    lang=self.lang,
                    config='--psm 3 --oem 3'
                )
            
            self.progress_update.emit(100)
            
            if not text.strip():
                self.result_ready.emit("Aucun texte n'a pu être extrait de cette image. Essayez d'ajuster les paramètres de prétraitement ou utilisez une image avec un texte plus clair.")
            else:
                self.result_ready.emit(text)
                
        except Exception as e:
            self.result_ready.emit(f"Erreur lors de l'extraction de texte: {str(e)}\n\nAssurez-vous que Tesseract OCR est correctement installé.")

class OCRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.setWindowTitle("Ready - Reconnaissance de texte")
        self.setWindowIcon(QIcon("readycon.png"))
        self.setMinimumSize(900, 650)
        
        # Style amélioré avec thème moderne
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QLabel {
                font-family: 'Segoe UI', Arial;
                color: #212529;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a58ca;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                min-height: 25px;
            }
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
                padding: 8px;
                background-color: white;
            }
            QFrame {
                border-radius: 8px;
                background-color: white;
                border: 1px solid #e9ecef;
            }
            QProgressBar {
                border: 1px solid #ced4da;
                border-radius: 4px;
                text-align: center;
                height: 15px;
            }
            QProgressBar::chunk {
                background-color: #0d6efd;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ced4da;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                font-family: 'Segoe UI', Arial;
                color: #212529;
            }
            QSlider::groove:horizontal {
                border: 1px solid #ced4da;
                height: 8px;
                background: #f8f9fa;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0d6efd;
                border: 1px solid #0d6efd;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
        """)

        # Création du widget central et layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # En-tête de l'application
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #0d6efd; border-radius: 8px; border: none;")
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Ready")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        desc_label = QLabel("Reconnaissance de texte dans les images - Simple et puissant")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 14px; color: white; margin-bottom: 5px;")
        header_layout.addWidget(desc_label)
        
        main_layout.addWidget(header_frame)
        
        # Layout pour l'image et le texte (côte à côte)
        content_layout = QHBoxLayout()
        
        # Panneau pour l'image
        image_frame = QFrame()
        image_frame.setObjectName("imageFrame")
        image_frame.setStyleSheet("#imageFrame { padding: 15px; }")
        image_layout = QVBoxLayout(image_frame)
        
        # Titre de la section
        image_title = QLabel("Image source")
        image_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0d6efd;")
        image_layout.addWidget(image_title)
        
        # Label pour l'image
        self.image_label = QLabel("Aucune image sélectionnée")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(250)
        self.image_label.setStyleSheet("background-color: #f8f9fa; border: 2px dashed #ced4da; border-radius: 5px;")
        image_layout.addWidget(self.image_label)
        
        # Bouton pour sélectionner une image
        self.select_btn = QPushButton("Sélectionner une image")
        self.select_btn.setIcon(QIcon("icon.png"))  # Ajoutez une icône si disponible
        self.select_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.select_btn)

        # Options de traitement
        options_group = QGroupBox("Options d'extraction")
        options_layout = QVBoxLayout(options_group)
        
        # Choix de la langue
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Langue du texte:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "Français (fra)", 
            "Anglais (eng)", 
            "Espagnol (spa)", 
            "Allemand (deu)", 
            "Italien (ita)",
            "Multi-langues (fra+eng)"
        ])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        options_layout.addLayout(lang_layout)
        
        # Option de prétraitement
        preproc_layout = QHBoxLayout()
        self.preproc_check = QCheckBox("Utiliser le prétraitement d'image")
        self.preproc_check.setChecked(True)
        self.preproc_check.stateChanged.connect(self.toggle_image_controls)
        preproc_layout.addWidget(self.preproc_check)
        options_layout.addLayout(preproc_layout)
        
        # Contrôles d'image (luminosité/contraste)
        image_controls_layout = QVBoxLayout()
        
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Luminosité:")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-50, 50)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_value = QLabel("0")
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value.setText(str(v)))
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value)
        image_controls_layout.addLayout(brightness_layout)
        
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contraste:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-50, 50)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setTickPosition(QSlider.TicksBelow)
        self.contrast_value = QLabel("0")
        self.contrast_slider.valueChanged.connect(lambda v: self.contrast_value.setText(str(v)))
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_value)
        image_controls_layout.addLayout(contrast_layout)
        
        options_layout.addLayout(image_controls_layout)
        image_layout.addWidget(options_group)
        
        # Bouton d'extraction
        self.extract_btn = QPushButton("Extraire le texte")
        self.extract_btn.setEnabled(False)
        self.extract_btn.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                font-size: 14px;
                padding: 12px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #157347;
            }
            QPushButton:pressed {
                background-color: #146c43;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.extract_btn.clicked.connect(self.extract_text)
        image_layout.addWidget(self.extract_btn)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        image_layout.addWidget(self.progress_bar)
        
        # Panneau pour le texte
        text_frame = QFrame()
        text_frame.setObjectName("textFrame")
        text_frame.setStyleSheet("#textFrame { padding: 15px; }")
        text_layout = QVBoxLayout(text_frame)
        
        # Titre de la section
        text_title = QLabel("Texte extrait")
        text_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0d6efd;")
        text_layout.addWidget(text_title)
        
        # Zone de texte pour afficher le résultat
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("Le texte extrait de l'image apparaîtra ici")
        self.text_edit.setMinimumHeight(350)
        text_layout.addWidget(self.text_edit)
        
        # Boutons pour le texte
        text_btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("Copier le texte")
        self.copy_btn.clicked.connect(self.copy_text)
        self.copy_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Enregistrer en TXT")
        self.save_btn.clicked.connect(self.save_text)
        self.save_btn.setEnabled(False)
        
        text_btn_layout.addWidget(self.copy_btn)
        text_btn_layout.addWidget(self.save_btn)
        text_layout.addLayout(text_btn_layout)
        
        # Ajout des deux panneaux au layout principal
        content_layout.addWidget(image_frame, 40)
        content_layout.addWidget(text_frame, 60)
        main_layout.addLayout(content_layout)
        
        # Footer
        footer_frame = QFrame()
        footer_frame.setStyleSheet("background-color: #f8f9fa; border: none;")
        footer_layout = QHBoxLayout(footer_frame)
        
        footer_label = QLabel("© 2025 Ready - Développé avec PyQt5 et Tesseract OCR par LeChamoisDev")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        footer_layout.addWidget(footer_label)
        
        main_layout.addWidget(footer_frame)
        
        self.setCentralWidget(central_widget)
        
        # Variables pour stocker les données
        self.current_image_path = None
        self.ocr_thread = None
    
    def toggle_image_controls(self, state):
        enabled = (state == Qt.Checked)
        self.brightness_slider.setEnabled(enabled)
        self.contrast_slider.setEnabled(enabled)
        self.brightness_value.setEnabled(enabled)
        self.contrast_value.setEnabled(enabled)
    
    def select_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Sélectionner une image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # Afficher l'image
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Redimensionner pour s'adapter au label tout en conservant les proportions
                max_height = self.image_label.height() - 10  # Marge
                max_width = self.image_label.width() - 10    # Marge
                
                pixmap = pixmap.scaled(
                    max_width, 
                    max_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(pixmap)
                self.extract_btn.setEnabled(True)
                
                # Afficher le nom du fichier
                filename = os.path.basename(file_path)
                self.setWindowTitle(f"Ready - {filename}")
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger l'image.")
    
    def extract_text(self):
        if not self.current_image_path:
            return
        
        # Obtenir le code de langue du texte sélectionné
        selected_lang = self.lang_combo.currentText()
        lang_code = selected_lang.split("(")[1].split(")")[0]
        
        # Obtenir les paramètres de prétraitement
        use_preprocessing = self.preproc_check.isChecked()
        brightness = self.brightness_slider.value() if use_preprocessing else 0
        contrast = self.contrast_slider.value() if use_preprocessing else 0
        
        # Désactiver les boutons pendant le traitement
        self.extract_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        
        # Vider le texte précédent
        self.text_edit.clear()
        
        # Afficher un message d'attente
        self.text_edit.setPlaceholderText("Extraction en cours... Veuillez patienter...")
        
        # Afficher la barre de progression
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Vérifier que Tesseract est installé et accessible
        try:
            # Créer et démarrer le thread
            self.ocr_thread = OcrThread(
                self.current_image_path, 
                lang_code,
                use_preprocessing,
                brightness,
                contrast
            )
            self.ocr_thread.result_ready.connect(self.display_result)
            self.ocr_thread.progress_update.connect(self.update_progress)
            self.ocr_thread.start()
        except Exception as e:
            self.display_result(f"Erreur: {str(e)}\n\nVérifiez que Tesseract OCR est correctement installé sur votre système.")
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def display_result(self, text):
        # Afficher le texte extrait
        self.text_edit.setPlaceholderText("Le texte extrait de l'image apparaîtra ici")
        self.text_edit.setText(text)
        
        # Réactiver les boutons
        self.extract_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.copy_btn.setEnabled(bool(text))
        self.save_btn.setEnabled(bool(text))
        
        # Cacher la barre de progression
        self.progress_bar.setVisible(False)
    
    def copy_text(self):
        # Copier le texte dans le presse-papier
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        
        # Notification plus élégante
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Information")
        msg.setText("Texte copié dans le presse-papier")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def save_text(self):
        if not self.text_edit.toPlainText():
            return
            
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Enregistrer le texte", "", 
            "Fichiers texte (*.txt)"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            
            # Notification plus élégante
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Information")
            msg.setText(f"Texte enregistré avec succès")
            msg.setInformativeText(f"Le fichier a été sauvegardé à l'emplacement suivant :\n{file_path}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

if __name__ == "__main__":
    # Vérifier et configurer Tesseract
    try:
        # Sur Windows, décommentez et adaptez cette ligne si nécessaire:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Vérifier la version de Tesseract
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            print(f"Tesseract OCR version: {tesseract_version}")
        except:
            print("Avertissement: Impossible de détecter la version de Tesseract. Assurez-vous qu'il est correctement installé.")
        
        app = QApplication(sys.argv)
        window = OCRApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erreur au démarrage: {str(e)}")
        
        # Afficher un message d'erreur graphique si possible
        try:
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Erreur de démarrage")
            msg.setText("Impossible de démarrer l'application")
            msg.setInformativeText(f"Erreur: {str(e)}\n\nAssurez-vous que Tesseract OCR est correctement installé sur votre système.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except:
            pass