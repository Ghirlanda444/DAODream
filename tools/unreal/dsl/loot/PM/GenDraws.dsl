(fn GenDraws ()
  (Variabili|Predefinito|ImpostaGF (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 2))
  (Variabili|Predefinito|ImpostaGN 0)
  (Variabili|Predefinito|ImpostaGNMax (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 2)))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Variabili|Predefinito|OttieniGNMax)
    (:LoopBody
      (Funzionedichiamata|GenNumOne))
    (:Completed
      (Funzionedichiamata|GenDraws2))))
