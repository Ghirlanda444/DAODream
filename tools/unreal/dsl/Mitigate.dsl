(fn Mitigate (Scale Pen Bonus Armour)
  (Variabili|Predefinito|ImpostaLastDamage (Utility|Operatori|Aggiungi (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniLastRoll) (Matematica|Float|Max(Float) (Utility|Operatori|Sottrai (Utility|Operatori|Moltiplica Armour (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 0.3) 0.7)) Pen) 0.0)) Bonus))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) Scale 0.0) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastDamage) (Variabili|Predefinito|OttieniDmgThreshold)))
    (:then
      (Variabili|Predefinito|ImpostaLastDamage (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniLastDamage) Scale))
      (Funzionedichiamata|FloorDamage))
    (:else
      (Funzionedichiamata|FloorDamage))))
