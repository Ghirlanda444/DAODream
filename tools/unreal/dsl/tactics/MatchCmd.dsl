(fn MatchCmd (C K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmds) (Utility|Operatori|Moltiplica K (Utility|Operatori|Aggiungi (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1))) C)
    (:then
      (Variabili|Predefinito|ImpostaSCmd (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmdNames) K)))))
