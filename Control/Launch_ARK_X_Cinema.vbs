Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

repoRoot = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = repoRoot

pythonw = "pythonw.exe"
script = fso.BuildPath(repoRoot, "Control\ark_cinema.py")
shell.Run pythonw & " """ & script & """", 0, False

Set fso = Nothing
Set shell = Nothing
