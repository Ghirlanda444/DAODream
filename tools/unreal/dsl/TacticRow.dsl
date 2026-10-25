(fn TacticRow (I)
  (Variabili|Predefinito|ImpostaRB (Utility|Operatori|Moltiplica I 6))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniTacDone)) (Utility|Operatori|Maggioreuguale(>=) I (Variabili|Predefinito|OttieniTacNext))) (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 5)) 0.0))
    (:then
      (Funzionedichiamata|TacticCond)
      (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniCondOk) (Utility|Operatori|Minoreuguale(<=) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTactics) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRB) 5))))
        (:then
          (Funzionedichiamata|TacticAct :I I))))))
