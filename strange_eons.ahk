Run setGenerator.seproject
Sleep 10000
WinGetPos, X, Y, W, H, A
While (X > 0) {
  Sleep 1000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000
WinGetPos, X, Y, W, H, A
While (X > 0) {
  Sleep 1000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000
WinGetPos, X, Y, W, H, A
While (X > 0) {
  Sleep 1000
  WinGetPos, X, Y, W, H, A
}
Sleep 5000
Send {Tab}
Sleep 1000
Send {Tab}
Sleep 1000
Send {Tab}
Sleep 1000
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
Send {F5}
While (!FileExist("makeCards_FINISHED")) {
  Sleep 1000
}
Sleep 5000
Send ^{F4}
Sleep 1000
Send {Tab}
Sleep 1000
Send {Tab}
Sleep 1000
Send {Tab}
Sleep 1000
Send {Up}
Sleep 1000
Send {Left}
Sleep 1000
Send {Up}
Sleep 1000
Send !{F4}
Exit