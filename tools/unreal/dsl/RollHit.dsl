(fn RollHit (DmgMin DmgMax Scale Pen Bonus Armour)
  (Variabili|Predefinito|ImpostaLastRoll (Matematica|Casuale|RandomFloatInRange DmgMin DmgMax))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniLastCrit)
    (:then
      (Variabili|Predefinito|ImpostaLastRoll (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniLastRoll) 1.5))
      (Variabili|Predefinito|ImpostaCrits (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniCrits) 1))
      (Funzionedichiamata|Mitigate :Scale Scale :Pen Pen :Bonus Bonus :Armour Armour))
    (:else
      (Funzionedichiamata|Mitigate :Scale Scale :Pen Pen :Bonus Bonus :Armour Armour))))
