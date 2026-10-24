(fn StrikeFoe ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|StrikePlayer (Variabili|Predefinito|OttieniMgr) :Attacker (Variabili|Ottieniunriferimentoasestesso) :Atk (Variabili|Predefinito|OttieniAttack) :DmgMin (Variabili|Predefinito|OttieniDmgMin) :DmgMax (Variabili|Predefinito|OttieniDmgMax) :Scale (Variabili|Predefinito|OttieniDmgScale) :Crit (Variabili|Predefinito|OttieniCrit) :Pen (Variabili|Predefinito|OttieniPen) :Bonus (Variabili|Predefinito|OttieniDmgBonus) :Flank (Variabili|Predefinito|OttieniFlank)))
    (:else
      (Funzionedichiamata|StrikeNpcFoe))))
