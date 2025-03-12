[![Download Ready](https://img.shields.io/badge/Download-Ready-blue?style=for-the-badge&logo=dropbox)](https://www.dropbox.com/scl/fi/c0134kytek3nrf8lyy6f4/Ready.exe?rlkey=1in50f30rwwfpupj1uv2umlla&st=qp0w0adl&dl=1)

# Ready - Text Recognition

Ready is an Optical Character Recognition (OCR) application that extracts text from images. It uses PyQt5 for the graphical interface and Tesseract OCR for text analysis.

## Installation

1. Go to [lechamois.github.io/downloads.html](https://lechamois.github.io/downloads.html).
2. Download the latest version of Ready.
3. Alternatively, download Ready directly from Dropbox on the top of Readme.
4. Make sure Tesseract OCR is installed on your Windows 10/11 system:
   - Download and install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).

## Usage

1. Launch the Ready application.
2. Click **Select an image** to choose an image file (PNG, JPG, BMP, etc.).
3. Configure the extraction options:
   - Select the language of the text to extract.
   - Enable or disable image preprocessing.
   - Adjust brightness and contrast if needed.
4. Click **Extract text** to start the analysis.
5. The extracted text will appear in the text area. You can:
   - Copy the text to the clipboard.
   - Save the text as a `.txt` file.

## Common Issues

- **No text detected**: Try enabling preprocessing and adjusting brightness/contrast.
- **Tesseract error (not found)**: Ensure Tesseract OCR is installed and correctly configured.
- **Application does not start**: Make sure all required Python dependencies are installed.

## Dependencies

- Python 3.x
- PyQt5
- OpenCV
- NumPy
- PIL (Pillow)
- Tesseract OCR

## License

Ready is an open-source project under the MIT license.

---

Enjoy using Ready for quick and easy text extraction! 🚀
