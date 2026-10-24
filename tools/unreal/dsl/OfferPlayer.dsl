(fn OfferPlayer (Hostile)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Variabili|Predefinito|OttieniGameOver))
    (:else
      (Funzionedichiamata|FoeOffer :Cand (Gioco|GetPlayerPawn 0) :Dist (Trasformazione|GetHorizontalDistanceTo Hostile (Gioco|GetPlayerPawn 0))))))
