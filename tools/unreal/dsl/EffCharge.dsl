(fn EffCharge (K)
  (Funzionedichiamata|HitFoe :Bonus 0.0 :Mul 1.0 :bOff "false" :bSure "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) 0.0)
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
        (:then
          (Classe|BPPlotManager|StunPlayer (Variabili|Predefinito|OttieniMgr) :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7)) :bFall "true"))
        (:else
          (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
          (Funzionedichiamata|KnockResist _npc :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7))))))))
