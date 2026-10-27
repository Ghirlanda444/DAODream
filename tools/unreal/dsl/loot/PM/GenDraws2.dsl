(fn GenDraws2 ()
  (Variabili|Predefinito|ImpostaGN (Matematica|Intero|SelectInt 1 (Variabili|Predefinito|OttieniGN) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 8) 0.5) (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniGN) 1))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniGN) 1)
    (:LoopBody
      (Funzionedichiamata|GenDrawOne))))
