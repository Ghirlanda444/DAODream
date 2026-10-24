(fn StrikeFoe ()
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniFoe)))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _npc)
    (:then
      (Funzionedichiamata|TakeStrike _npc :Attacker (Variabili|Ottieniunriferimentoasestesso) :InAttack (Variabili|Predefinito|OttieniAttack) :InMin (Variabili|Predefinito|OttieniDmgMin) :InMax (Variabili|Predefinito|OttieniDmgMax) :InScale (Variabili|Predefinito|OttieniDmgScale) :InCrit (Variabili|Predefinito|OttieniCrit) :InPen (Variabili|Predefinito|OttieniPen) :InBonus (Variabili|Predefinito|OttieniDmgBonus) :InFlank (Variabili|Predefinito|OttieniFlank)))
    (:else
      (Classe|BPPlotManager|StrikePlayer (Variabili|Predefinito|OttieniMgr) :Attacker (Variabili|Ottieniunriferimentoasestesso) :Atk (Variabili|Predefinito|OttieniAttack) :DmgMin (Variabili|Predefinito|OttieniDmgMin) :DmgMax (Variabili|Predefinito|OttieniDmgMax) :Scale (Variabili|Predefinito|OttieniDmgScale) :Crit (Variabili|Predefinito|OttieniCrit) :Pen (Variabili|Predefinito|OttieniPen) :Bonus (Variabili|Predefinito|OttieniDmgBonus) :Flank (Variabili|Predefinito|OttieniFlank)))))
