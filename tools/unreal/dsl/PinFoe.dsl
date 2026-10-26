(fn PinFoe (Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|StunPlayer (Variabili|Predefinito|OttieniMgr) :Seconds Seconds :bFall "false"))
    (:else
      (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
      (Funzionedichiamata|Pin _npc :Seconds Seconds))))
