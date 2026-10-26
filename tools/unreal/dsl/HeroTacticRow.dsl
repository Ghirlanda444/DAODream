(fn HeroTacticRow (I)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniHTDone) (Variabili|Predefinito|OttieniHTStop)) (Utility|Operatori|Minoreuguale(<=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 5)) 0.0))
    (:else
      (Funzionedichiamata|HeroTacticCond :I I)
      (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniHTCond) (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 5))))
        (:then
          (Funzionedichiamata|HeroTacticUse :I I))))))
