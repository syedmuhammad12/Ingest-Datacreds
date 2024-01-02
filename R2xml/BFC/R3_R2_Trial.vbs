'--------------------------------------------------------------------------------------------------------------------------
'Configuration
'--------------------------------------------------------------------------------------------------------------------------
filePathR2 = "C:\Users\Bhawani.Shankar\Desktop\r2\"
filePathR2_Archive = "C:\Users\Bhawani.Shankar\Desktop\r2_archive\"
filePathR3 = "C:\Users\Bhawani.Shankar\Desktop\r3\"
filePathR3_Archive = "C:\Users\Bhawani.Shankar\Desktop\r3_archive\"
filePathTemp = "C:\Users\Bhawani.Shankar\Desktop\Temp\"

'--------------------------------------------------------------------------------------------------------------------------
Set oShell = CreateObject ("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")


'Convert R3 files(copied to Temp folder) to R2 folder.
Set fldr = objFSO.GetFolder(filePathTemp)
Set Collec_Files= fldr.Files
MsgBox Collec_Files.Count
For Each File in Collec_Files
	filePathFrom = filePathTemp & File.Name
	filePathTo = filePathR2 & File.Name
	Msgbox filePathFrom
	MsgBox filePathTo
	oShell.Run "msxsl """&filePathFrom&""" downgrade-icsr.xsl -o """&filePathTo&""" "
Next
Set Collec_Files = Nothing
Set fldr = Nothing

Set objFSO = Nothing

MsgBox "R3 to R2 Done"