(fn DeathBlow (Target)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|Array|ContainsItem (Variabili|Predefinito|OttieniPassives) 3021.0) (Matematica|Booleano|ANDBoolean (Classe|BPDlgNPC|OttieniDead Target) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastDamage) 0.0)))
    (:then
      (Variabili|Predefinito|ImpostaPStamina (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPStamina) (Utility|Operatori|Moltiplica (Classe|BPDlgNPC|OttieniMaxHealth Target) 0.2)) (Variabili|Predefinito|OttieniPPool)))
      (Funzionedichiamata|ShowStamina))))
