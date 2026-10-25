(fn TakeAttack (InAttack InMin InMax InScale InThreshold)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDead)
    (:else
      (Classe|BPPlotManager|PlayerStrike (Variabili|Predefinito|OttieniMgr) :Target (Variabili|Ottieniunriferimentoasestesso) :Def (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniDefense) (Variabili|Predefinito|OttieniNOwnDef)) :Armour (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniArmour) (Variabili|Predefinito|OttieniNOwnArmour))))))
