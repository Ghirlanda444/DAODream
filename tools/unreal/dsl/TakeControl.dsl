(fn TakeControl ()
  (Funzionedichiamata|Recenter)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|SetControlled _a :bOn "false"))
  (Variabili|Predefinito|ImpostaHeroTarget)
  (Variabili|Predefinito|ImpostaHeroUse)
  (Variabili|Predefinito|ImpostaMoving "false")
  (Input|ResetIgnoreMoveInput (Gioco|GetPlayerController 0))
  (IA|Navigazione|StopMovement (Gioco|GetPlayerController 0))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (Classe|BPDlgNPC|SetControlled (Variabili|Predefinito|OttieniSelected) :bOn "true")
      (Input|SetIgnoreMoveInput (Gioco|GetPlayerController 0) :bNewMoveInput "true")
      (Trasformazione|AttachComponentToComponent :self (Attore|GetComponentbyClass (Gioco|GetPlayerPawn 0) "/Script/Engine.SpringArmComponent") :Parent (Classe|BPDlgNPC|OttieniBody (Variabili|Predefinito|OttieniSelected)) :LocationRule "KeepRelative" :RotationRule "KeepRelative" :ScaleRule "KeepRelative" :bWeldSimulatedBodies "false"))
    (:else
      (Trasformazione|AttachComponentToComponent :self (Attore|GetComponentbyClass (Gioco|GetPlayerPawn 0) "/Script/Engine.SpringArmComponent") :Parent (Attore|GetComponentbyClass (Gioco|GetPlayerPawn 0) "/Script/Engine.CapsuleComponent") :LocationRule "KeepRelative" :RotationRule "KeepRelative" :ScaleRule "KeepRelative" :bWeldSimulatedBodies "false"))))
