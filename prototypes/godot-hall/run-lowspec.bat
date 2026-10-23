@echo off
rem Runs the hall on Godot's lightweight Compatibility renderer (OpenGL 3.3),
rem the one meant for older and weaker PCs.
rem Set GODOT to the full path of your Godot 4.7 exe, or put the exe in this folder.
if "%GODOT%"=="" for %%f in ("%~dp0Godot*.exe") do set "GODOT=%%f"
if "%GODOT%"=="" (
  echo Set GODOT to the full path of your Godot 4.7 exe, then run this again.
  pause
  exit /b 1
)
"%GODOT%" --path "%~dp0." --rendering-method gl_compatibility
