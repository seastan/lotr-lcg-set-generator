FileRead, LogPath, remote_logs_path
LogPath := LogPath "\autohotkey.log"

WriteLog(LogPath, "starting")

If (FileExist("makeCards_FINISHED")) {
  WriteLog(LogPath, "ERROR makeCards script already finished, exiting")
  Exit
}

Timeout := 7200000
StartTime := A_TickCount

WriteLog(LogPath, "opening Strange Eons project")
Run setGenerator.seproject
Sleep 10000

WinGetPos, X, Y, W, H, A
While (X > 0) {
  If (A_TickCount - StartTime > Timeout) {
    WriteLog(LogPath, "ERROR reached the timeout, exiting")
    Exit
  }
  WriteLog(LogPath, "waiting for no popups (1/3)")
  Sleep 5000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000

WinGetPos, X, Y, W, H, A
While (X > 0) {
  If (A_TickCount - StartTime > Timeout) {
    WriteLog(LogPath, "ERROR reached the timeout, exiting")
    Exit
  }
  WriteLog(LogPath, "waiting for no popups (2/3)")
  Sleep 5000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000

WinGetPos, X, Y, W, H, A
While (X > 0) {
  If (A_TickCount - StartTime > Timeout) {
    WriteLog(LogPath, "ERROR reached the timeout, exiting")
    Exit
  }
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
  If (A_TickCount - StartTime > Timeout) {
    WriteLog(LogPath, "ERROR reached the timeout, exiting")
    Exit
  }
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
  FileAppend, % A_YYYY "-" A_MM "-" A_DD " " A_Hour ":" A_Min ":" A_Sec " " Text "`n", %LogPath%
}
