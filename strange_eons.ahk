FileRead, LogPath, remote_logs_path
LogPath := LogPath "\autohotkey.log"

WriteLog(LogPath, "starting")

If (FileExist("makeCards_FINISHED")) {
  WriteLog(LogPath, "makeCards script already finished, exiting")
  Exit
}

WriteLog(LogPath, "opening Strange Eons project")
Run setGenerator.seproject
Sleep 10000

WinGetPos, X, Y, W, H, A
While (X > 0) {
  WriteLog(LogPath, "waiting for no popups (1/3)")
  Sleep 5000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000

WinGetPos, X, Y, W, H, A
While (X > 0) {
  WriteLog(LogPath, "waiting for no popups (2/3)")
  Sleep 5000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000

WinGetPos, X, Y, W, H, A
While (X > 0) {
  WriteLog(LogPath, "waiting for no popups (3/3)")
  Sleep 5000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000

WriteLog(LogPath, "entering the folder tree")
Send {Tab}
Sleep 1000
Send {Tab}
Sleep 1000
Send {Tab}
Sleep 1000

WriteLog(LogPath, "collapsing possibly opened folders")
Send {Down}
Sleep 1000
Send {Left}
Sleep 1000
Send {PgUp}
Sleep 1000

Send {Down}
Sleep 1000
Send {Down}
Sleep 1000
Send {Left}
Sleep 1000
Send {PgUp}
Sleep 1000

Send {Down}
Sleep 1000
Send {Down}
Sleep 1000
Send {Down}
Sleep 1000
Send {Left}
Sleep 1000
Send {PgUp}

WriteLog(LogPath, "navigating to the script")
Send {Down}
Sleep 1000
Send {Down}
Sleep 1000
Send {Down}
Sleep 1000
Send {Right}
Sleep 1000
Send {Down}
Sleep 1000
Send {Enter}
Sleep 1000

WriteLog(LogPath, "running the script")
Send {F5}

While (!FileExist("makeCards_FINISHED")) {
  WriteLog(LogPath, "waiting for successful script finish")
  Sleep 30000
}
Sleep 5000

WriteLog(LogPath, "closing the script and Strange Eons")
Send ^{F4}
Sleep 1000
Send !{F4}

WriteLog(LogPath, "exiting")
Exit

WriteLog(LogPath, Text) {
  FormatTime, CurrentTime
  FileAppend, % CurrentTime " " Text "`n", %LogPath%
}