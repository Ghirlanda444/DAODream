(fn Regen (Amount)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniInParty) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead)))
    (:then
      (Variabili|Predefinito|ImpostaHealth (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniHealth) Amount) (Variabili|Predefinito|OttieniMaxHealth)))
      (Funzionedichiamata|UpdateBar))))
