(fn TacMake ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTac))
    (:else
      (bind _w (InterfacciaUtente|Creawidget "/Game/Cousland/Combat/WBP_Tactics.WBP_Tactics_C" (Gioco|GetPlayerController 0)))
      (bind _t (Utilità|Casting|CastToWBP_Tactics _w))
      (Variabili|Predefinito|ImpostaTac _t))))
