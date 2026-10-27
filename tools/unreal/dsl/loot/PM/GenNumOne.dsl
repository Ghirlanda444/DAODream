(fn GenNumOne ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniGF) 0.0)
    (:then
      (Variabili|Predefinito|ImpostaGR (Matematica|Casuale|RandomFloat))
      (Variabili|Predefinito|ImpostaGN (Matematica|Intero|SelectInt (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniGN) 1) (Variabili|Predefinito|OttieniGN) (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniGR) (Variabili|Predefinito|OttieniGF))))
      (Variabili|Predefinito|ImpostaGF (Utility|Operatori|Sottrai (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniGF) (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniGR) 0.0 (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniGR) (Variabili|Predefinito|OttieniGF)))) 1.0)))))
