(fn TrCtrl ()
  (Variabili|Predefinito|ImpostaTCtrl (Gioco|GetPlayerPawn 0))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (Variabili|Predefinito|ImpostaTCtrl (Variabili|Predefinito|OttieniSelected)))))
