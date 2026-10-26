(fn MoveKeys (X Y)
  (Funzionedichiamata|Recenter)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (bind (_fx _fy _fz) (Matematica|Vettore|BreakVector (Matematica|Vettore|GetForwardVector (Telecamera|GetCameraRotation :self (Gioco|GetPlayerCameraManager 0)))))
      (bind (_rx _ry _rz) (Matematica|Vettore|BreakVector (Matematica|Vettore|GetRightVector (Telecamera|GetCameraRotation :self (Gioco|GetPlayerCameraManager 0)))))
      (Classe|BPDlgNPC|ManualMove (Variabili|Predefinito|OttieniSelected) :Dir (Matematica|Vettore|Normalize (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Matematica|Vettore|MakeVector _fx _fy 0.0) Y) (Utility|Operatori|Moltiplica (Matematica|Vettore|MakeVector _rx _ry 0.0) X)))))))
