from vb2py.vbfunctions import *
from vb2py.vbdebug import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from pathlib import Path
import os
import win32com.client
import pythoncom
from data_ingestion import settings


class Config(APIView):
    def get(self, request):
        # try:
            basepath = settings.STATICFILES_LOCAL
            filePathR3 = Path(os.path.join(basepath, 'r3'))
            if not filePathR3.exists():
                filePathR3.mkdir()

            filePathR3_Archive = Path(os.path.join(basepath, 'r3_archive'))
            if not filePathR3_Archive.exists():
                filePathR3_Archive.mkdir()

            filePathR2 = Path(os.path.join(basepath, 'r2'))
            if not filePathR2.exists():
                filePathR2.mkdir()

            filePathR2_Archive = Path(os.path.join(basepath, 'r2_archive'))
            if not filePathR2_Archive.exists():
                filePathR2_Archive.mkdir()

            filePathTemp = Path(os.path.join(basepath, 'Temp'))
            if not filePathTemp.exists():
                filePathTemp.mkdir()

            filePathLog = Path(os.path.join(basepath, 'Log'))
            if not filePathLog.exists():
                filePathLog.mkdir()

            filePathConverted = Path(os.path.join(basepath, 'Converted'))
            if not filePathConverted.exists():
                filePathConverted.mkdir()

            now = datetime.utcnow()
            strDateTime = now.strftime("%d%B%Y_%H_%M_%S")
            filePathR3_Archive = Path(os.path.join(filePathR3_Archive, 'R3_Archive_{}'.format(strDateTime)))
            filePathR2_Archive = Path(os.path.join(filePathR2_Archive, 'R2_Archive_{}'.format(strDateTime)))
            #--------------------------------------------------------------------------------------------------------------------------
            # oShell = CreateObject("WScript.Shell")
            oShell = win32com.client.Dispatch("Excel.Application", pythoncom.CoInitialize())

            objFile = open(Path(os.path.join(filePathLog, 'Log_{}.txt'.format(strDateTime))), 'w+')


            # objFSO = CreateObject('Scripting.FileSystemObject')
            # filesys = objFSO
            # objFile = objFSO.CreateTextFile(os.path.join(filePathLog, 'Log_{}.txt'.format(strDateTime)))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} Log File Created.\r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} Creating folders for Converted/R2 and Converted/R3.\r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            if not Path(os.path.join(filePathConverted, 'R2')).exists():
                Path(os.path.join(filePathConverted, 'R2')).mkdir()

            if not Path(os.path.join(filePathConverted, 'R3')).exists():
                Path(os.path.join(filePathConverted, 'R3')).mkdir()

            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} Created folders for Converted/R2 and Converted/R3 \r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} Start of moving files from R2 folder to Temp folder. \r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')

            #Move files from R2 folder to Temp
            if Path(filePathR2).exists():
                Collec_Files = os.listdir(filePathR2)
                objFile.write('{} Number of files to be moved from R2 folder to Temp are : {} \r\n'.format(now, len(Collec_Files)))
                for strFileName in Collec_Files:
                    os.replace(Path(os.path.join(filePathR2, strFileName)), Path(os.path.join(filePathTemp, strFileName)))
                    objFile.write('{} {} File moved from R2 folder to Temp folder.\r\n'.format(now, strFileName))
                Collec_Files = None

            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} End of moving files from R2 folder to Temp folder.\r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} Start of Conversion of R2 to R3 files.\r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            
            #Convert R2 files(copied to Temp folder) to R3 Archive folder.

            if Path(filePathTemp).exists():
                Collec_Files = os.listdir(filePathTemp)
                objFile.write('{} Number of files to be converted from R2 to R3 are : {}\r\n'.format(now, len(Collec_Files)))
                for strFileName in Collec_Files:
                    filePathFrom = Path(os.path.join(filePathTemp, strFileName))
                    filePathTo = Path(os.path.join(filePathConverted, 'R3', strFileName))
                    returnSt = oShell.Run("msxsl {} converter_files/upgrade-icsr.xsl -o {}".format(filePathFrom, filePathTo), 0, True)
                    if returnSt == 0:
                        objFile.write('{} {} File converted from R2 to R3.\r\n'.format(now, strFileName))
                    else:
                        objFile.write('{} {} File not converted.\r\n'.format(now, strFileName))
                Collec_Files = None

            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('{} End of conversion of R2 to R3 files.\r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write(' Start of archiving files from Temp to R2_Archive folder.\r\n'.format(now))
            objFile.write('---------------------------------------------------------------------------------------------------------------------\r\n')
            objFile.write('\r\n')
            return
            #Move files from Temp folder to R3_Archive
            fldr = objFSO.GetFolder(filePathTemp)
            if objFSO.FolderExists(fldr):
                objFSO.CreateFolder(filePathR2_Archive)
                Collec_Files = fldr.Files
                objFile.WriteLine(now + ' Number of files to be moved from Temp folder to R2_Archive are : ' + Collec_Files.Count)
                for File in Collec_Files:
                    strFileName = File.Name
                    objFSO.MoveFile(os.path.join(filePathTemp, File.Name), os.path.join(filePathR2_Archive, strFileName))
                    objFile.WriteLine(now + ' File moved from Temp folder to R2_Archive folder - ' + strFileName)
                Collec_Files = None
            fldr = None
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' End of archiving files from Temp to R2_Archive folder.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine('')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' Start of moving files from R3 folder to Temp folder.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            #Move files from R3 folder to Temp
            fldr = objFSO.GetFolder(filePathR3)
            if objFSO.FolderExists(fldr):
                Collec_Files = fldr.Files
                objFile.WriteLine(now + ' Number of files to be moved from R3 folder to Temp are : ' + Collec_Files.Count)
                for File in Collec_Files:
                    strFileName = File.Name
                    objFSO.MoveFile(os.path.join(filePathR3, File.Name), os.path.join(filePathTemp, strFileName))
                    objFile.WriteLine(now + ' File moved from R3 folder to Temp folder - ' + strFileName)
                Collec_Files = None
            fldr = None
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' End of moving files from R3 folder to Temp folder.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine('')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' Start of Conversion of R3 to R2 files.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            #Convert R3 files(copied to Temp folder) to R2 Archive folder.
            fldr = objFSO.GetFolder(filePathTemp)
            if objFSO.FolderExists(fldr):
                Collec_Files = fldr.Files
                objFile.WriteLine(now + ' Number of files to be converted from R3 to R2 are : ' + Collec_Files.Count)
                for File in Collec_Files:
                    strFileName = File.Name
                    filePathFrom = os.path.join(filePathTemp, strFileName)
                    filePathTo = os.path.join(filePathConverted, 'R2', strFileName)
                    returnSt = oShell.Run('msxsl "{}" converter_files/downgrade-icsr.xsl -o "{}" '.format(filePathFrom, filePathTo),0,True)
                    if returnSt == 0:
                        objFile.WriteLine(now + ' File converted from R3 to R2 are : ' + strFileName)
                    else:
                        objFile.WriteLine(now + ' File not converted : ' + strFileName)
                    #oShell.Run "msxsl """&filePathFrom&""" downgrade-icsr.xsl -o """&filePathTo&""" 2>Out1.txt",0,True
                Collec_Files = None
            fldr = None
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' End of conversion of R3 to R2 files.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine('')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' Start of archiving files from Temp to R3_Archive folder.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            #Move files from Temp folder to R3_Archive
            fldr = objFSO.GetFolder(filePathTemp)
            if objFSO.FolderExists(fldr):
                objFSO.CreateFolder(filePathR3_Archive)
                Collec_Files = fldr.Files
                objFile.WriteLine(now + ' Number of files to be moved from Temp folder to R3_Archive are : ' + Collec_Files.Count)
                for File in Collec_Files:
                    strFileName = File.Name
                    objFSO.MoveFile(os.path.join(filePathTemp, File.Name), os.path.join(filePathR3_Archive, strFileName))
                    objFile.WriteLine(now + ' File moved from Temp folder to R3_Archive folder - ' + strFileName)
                Collec_Files = None
            fldr = None
            objFSO = None
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' End of archiving files from Temp to R3_Archive folder.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine('')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.WriteLine(now + ' End of Log File.')
            objFile.WriteLine('---------------------------------------------------------------------------------------------------------------------')
            objFile.Close()
            objFile = None
            oShell.Run(os.path.join(filePathLog, 'Log_{}.txt'.format(strDateTime)))
            return Response({"error": 0, "msg": "Successfully Converted"}, status=status.HTTP_200_OK) 
        # except Exception as e:
        #     return Response({"error": 1, "msg": str(e)}, status=status.HTTP_200_OK) 
