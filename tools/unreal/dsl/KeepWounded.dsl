(fn KeepWounded (Who)
  (Variabili|Predefinito|ImpostaKeep "false")
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid Who)
    (:then
      (Funzionedichiamata|WhoHealth :Who Who)
      (Variabili|Predefinito|ImpostaKeep (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniWhoHp) 0.2) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniWhoHp) 0.1)) (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) 50.0)) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniWhoHp) 0.1) (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) 90.0)))))))
