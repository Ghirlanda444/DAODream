(fn TakeAttack (InAttack InMin InMax InScale InThreshold)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDead)
    (:else
      (Classe|BPPlotManager|PlayerStrike (Variabili|Predefinito|OttieniMgr) :Target (Variabili|Ottieniunriferimentoasestesso) :Def (Variabili|Predefinito|OttieniDefense) :Armour (Variabili|Predefinito|OttieniArmour)))))
