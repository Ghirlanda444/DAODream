(fn PickOffer (Npc Where)
  (bind _d (Matematica|Vettore|Distance2D(Vector) (Trasformazione|GetActorLocation Npc) Where))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) _d (Variabili|Predefinito|OttieniPickDist))
    (:then
      (Variabili|Predefinito|ImpostaPickDist _d)
      (Variabili|Predefinito|ImpostaPickNpc Npc))))
