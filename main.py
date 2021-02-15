import glob
import os
import img2pdf
import pdf2image as pdf2img
import PyPDF4
import pikepdf
import shutil
import sys
import pathlib


def resourcePath(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def flattenPDF(pdfFileName):
    pdfFile = pdf2img.convert_from_path(resourcePath(pdfFileName), 600, poppler_path='poppler\\bin')
    imageDirName = pdfFileName.replace(".pdf", "")
    os.mkdir(resourcePath(imageDirName))
    for i, page in enumerate(pdfFile):
        page.save(resourcePath(imageDirName + "\\" + pdfFileName + str(i) + "jpg"), "PNG")

    flattenedPDF = open(resourcePath("flattened_" + pdfFileName), "wb")
    pdfImages = []
    for img in os.listdir(imageDirName):
        imgFile = open(resourcePath(imageDirName + "\\" + img), 'rb')
        pdfImages.append(imgFile)

    res = img2pdf.convert(pdfImages)
    flattenedPDF.write(res)
    for imgFile in pdfImages:
        imgFile.close()


def watermarkingPDF(pdfFileName):
    pdfFile = open(resourcePath(pdfFileName), "rb")
    pdfFileReader = PyPDF4.PdfFileReader(pdfFile)
    resultPdfFile = open(resourcePath("watermarked_" + pdfFileName), "wb")
    watermarkImage = open(resourcePath("watermark.pdf"), 'rb')

    pdfFilePagesNum = pdfFileReader.getNumPages()
    pdfWriter = PyPDF4.PdfFileWriter()

    for i in range(pdfFilePagesNum):
        tmpPage = pdfFileReader.getPage(i)
        tmpwatermarkPage = PyPDF4.PdfFileReader(watermarkImage).getPage(0)
        tmpwatermarkPage.mergePage(tmpPage)
        pdfWriter.addPage(tmpwatermarkPage)

    pdfWriter.write(resultPdfFile)

    pdfFile.close()
    watermarkImage.close()
    resultPdfFile.close()


def encryptPDF(pdfFileName, password):
    pdfFile = pikepdf.open(resourcePath("flattened_watermarked_" + pdfFileName))
    pdfFile.save(resourcePath("protected_" + pdfFileName), encryption=pikepdf.Encryption(owner=password, user=password, R=6))
    pdfFile.close()


willWatermarking = input("워터마크를 넣으시겠습니까? (y/n) >> ")
willWatermarking.lower()

willimageConvert = input("이미지로 변환하시겠습니까? (y/n) >> ")
willimageConvert.lower()

password = input("비밀 번호를 입력하세요 >> ")

pdfList2 = glob.glob(resourcePath("*.pdf"))
pdfList = []
for i in pdfList2:
    pdfList.append(os.path.basename(i))

input()
for pdfFileName in pdfList:
    if (pdfFileName == "watermark.pdf"):
        continue
    if (willWatermarking == 'y'):
        print(pdfFileName + "워터마킹 시작")
        try:
            watermarkingPDF(pdfFileName)
        except Exception as ex:
            print(pdfFileName + " 워터마킹 에러")
            print(ex)
            continue
        print(pdfFileName + " 워터마킹 완료")

    if (willimageConvert == 'y'):
        print(pdfFileName + " 이미지 변환 시작")
        try:
            flattenPDF("watermarked_" + pdfFileName)
        except Exception as ex:
            print(pdfFileName + " 이미지 변환 에러")
            print(str(ex))
            continue
        print(pdfFileName + " 이미지 변환 완료")
    print(pdfFileName + " 암호화 시작")
    encryptPDF(pdfFileName, password)

    try:
        pass
    except:
        print(pdfFileName + " 암호화 에러")
        continue
    print(pdfFileName + " 암호화 완료")
    print(pdfFileName + " 쓰레기 청소")
    shutil.rmtree("watermarked_" + pdfFileName.replace(".pdf", ""))
    os.remove("watermarked_" + pdfFileName)
    os.remove("flattened_watermarked_" + pdfFileName)
