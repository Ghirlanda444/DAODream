(fn GCopy (InLoot O J)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Aggiungi O J) (Utilità|Array|Length InLoot))
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniGLoot) (Utilità|Array|Ottieni(unacopia) InLoot (Utility|Operatori|Aggiungi O J))))
    (:else
      (Utilità|Array|Add (Variabili|Predefinito|OttieniGLoot) 0.0))))
