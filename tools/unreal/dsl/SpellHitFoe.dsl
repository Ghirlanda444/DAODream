(fn SpellHitFoe (Amount)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|SpellHitPlayer (Variabili|Predefinito|OttieniMgr) :Amount Amount))
    (:else
      (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
      (Funzionedichiamata|TakeHit _npc :Damage Amount))))
