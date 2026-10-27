(fn GenDrawOne ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 0) 0.0)
    (:then
      (Variabili|Predefinito|ImpostaGTbl (Matematica|Float|Truncate (Matematica|Float|SelectFloat (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 1) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 0) (Utility|Operatori|Minoreuguale(<=) (Matematica|Casuale|RandomFloat) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 3)))))
      (Funzionedichiamata|GenDrawTbl))))
