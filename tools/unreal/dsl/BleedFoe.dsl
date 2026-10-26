(fn BleedFoe (Amount Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|BleedPlayer (Variabili|Predefinito|OttieniMgr) :Amount Amount :Seconds Seconds))
    (:else
      (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
      (Funzionedichiamata|Bleed _npc :Amount Amount :Seconds Seconds))))
