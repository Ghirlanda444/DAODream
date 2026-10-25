(fn OfferPlayer (Hostile)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Variabili|Predefinito|OttieniGameOver)) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPlayerAttackers) (Variabili|Predefinito|OttieniSlots)))
    (:else
      (Funzionedichiamata|FoeOffer :Cand (Gioco|GetPlayerPawn 0) :Dist (Trasformazione|GetHorizontalDistanceTo Hostile (Gioco|GetPlayerPawn 0))))))
