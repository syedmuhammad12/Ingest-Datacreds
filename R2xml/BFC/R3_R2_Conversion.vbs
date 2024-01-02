'--------------------------------------------------------------------------------------------------------------------------
'Configuration
'--------------------------------------------------------------------------------------------------------------------------
filePathR2 = "C:\BFC\r2\"
filePathR2_Archive = "C:\BFC\r2_archive\"
filePathR3 = "C:\BFC\r3\"
filePathR3_Archive = "C:\BFC\r3_archive\"
filePathTemp = "C:\BFC\Temp\"
filePathLog = "C:\BFC\Log\"

'--------------------------------------------------------------------------------------------------------------------------

strDateTime = Day(Now) & MonthName(Month(Now)) & Year(Now) & "_" & Hour(Now) & "_" & Minute(Now) & "_" & Second(Now)
filePathR2_Archive = filePathR2_Archive & "R2_Archive_" & strDateTime & "\"
filePathR3_Archive = filePathR3_Archive & "R3_Archive_" & strDateTime & "\"

Set oShell = CreateObject ("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objFile = objFSO.CreateTextFile(filePathLog & "Log_" & strDateTime & ".txt")

objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " Log File Created.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine("")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " Start Archiving of files from R2 folder to R2_Archive folder.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")

'Move files from R2 folder to R2_Archive
Set fldr= objFSO.GetFolder(filePathR2)
If objFSO.FolderExists(fldr) Then
	objFSO.CreateFolder(filePathR2_Archive)
	Set Collec_Files= fldr.Files
	objFile.WriteLine(Now & " Number of files to be moved from R2 folder to R2_Archive are : " & Collec_Files.Count)
	For Each File in Collec_Files
		strFileName = File.Name
		objFSO.MoveFile filePathR2 & File.Name,filePathR2_Archive & strFileName
		objFile.WriteLine(Now & " File moved from R2 folder to R2_Archive folder - " & strFileName)
	Next
	Set Collec_Files = Nothing
Else
End If
Set fldr = Nothing
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " End Archiving of files from R2 folder to R2_Archive folder.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine("")


objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " Start of moving files from R2 folder to Temp folder.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
'Move files from R3 folder to Temp
Set fldr= objFSO.GetFolder(filePathR3)
If objFSO.FolderExists(fldr) Then
	Set Collec_Files= fldr.Files
	objFile.WriteLine(Now & " Number of files to be moved from R3 folder to Temp are : " & Collec_Files.Count)
	For Each File in Collec_Files
		strFileName = File.Name
		objFSO.MoveFile filePathR3 & File.Name,filePathTemp & strFileName
		objFile.WriteLine(Now & " File moved from R3 folder to Temp folder - " & strFileName)
	Next
	Set Collec_Files = Nothing
Else
End If
Set fldr = Nothing
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " End of moving files from R2 folder to R2_Archive folder.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine("")


objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " Start of Conversion of R3 to R2 files.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
'Convert R3 files(copied to Temp folder) to R2 folder.
Set fldr = objFSO.GetFolder(filePathTemp)
If objFSO.FolderExists(fldr) Then
	Set Collec_Files= fldr.Files
	objFile.WriteLine(Now & " Number of files to be converted from R3 to R2 are : " & Collec_Files.Count)

	For Each File in Collec_Files
		strFileName = File.Name
		filePathFrom = filePathTemp & strFileName
		filePathTo = filePathR2 & strFileName
		return = oShell.Run("msxsl """&filePathFrom&""" downgrade-icsr.xsl -o """&filePathTo&""" ",0,True)
		If return = 0 Then
			objFile.WriteLine(Now & " File converted from R3 to R2 are : " & strFileName)
		Else
			objFile.WriteLine(Now & " File not converted : " & strFileName)
		End If
		'oShell.Run "msxsl """&filePathFrom&""" downgrade-icsr.xsl -o """&filePathTo&""" 2>Out1.txt",0,True
	Next
	Set Collec_Files = Nothing

Else
End If
Set fldr = Nothing
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " End of conversion of R3 to R2 files.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine("")


objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " Start of archiving files from Temp to R3_Archive folder.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
'Move files from Temp folder to R3_Archive
Set fldr= objFSO.GetFolder(filePathTemp)
If objFSO.FolderExists(fldr) Then
	objFSO.CreateFolder(filePathR3_Archive)
	Set Collec_Files= fldr.Files
	objFile.WriteLine(Now & " Number of files to be moved from Temp folder to R3_Archive are : " & Collec_Files.Count)
	For Each File in Collec_Files
		strFileName = File.Name
		objFSO.MoveFile filePathTemp & File.Name,filePathR3_Archive & strFileName
		objFile.WriteLine(Now & " File moved from Temp folder to R3_Archive folder - " & strFileName)
	Next
	Set Collec_Files = Nothing
Else
End If
Set fldr = Nothing
Set objFSO = Nothing
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " End of archiving files from Temp to R3_Archive folder.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine("")

objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")
objFile.WriteLine(Now & " End of Log File.")
objFile.WriteLine("---------------------------------------------------------------------------------------------------------------------")

objFile.Close
Set objFile = Nothing
oShell.Run filePathLog & "Log_" & strDateTime & ".txt"