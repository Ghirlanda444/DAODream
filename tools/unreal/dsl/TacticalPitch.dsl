(fn TacticalPitch ()
  (bind _t (Matematica|Float|Clamp(Float) (Utility|Operatori|Dividi (Utility|Operatori|Sottrai (Classe|SpringArmComponent|OttieniTargetArmLength (Attore|GetComponentbyClass (Gioco|GetPlayerPawn 0) "/Script/Engine.SpringArmComponent")) 400.0) 2100.0) 0.0 1.0))
  (bind (_roll _pitch _yaw) (Matematica|Rotatore|BreakRotator (Telecamera|GetCameraRotation :self (Gioco|GetPlayerCameraManager 0))))
  (Pedina|SetControlRotation :self (Gioco|GetPlayerController 0) :NewRotation (Matematica|Rotatore|MakeRotator 0.0 (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica _t 60.0) 15.0) -1.0) _yaw)))
