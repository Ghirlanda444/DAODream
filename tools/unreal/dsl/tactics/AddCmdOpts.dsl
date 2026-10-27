(fn AddCmdOpts (K)
  (Variabili|Predefinito|ImpostaCmdId (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmds) (Utility|Operatori|Moltiplica K (Utility|Operatori|Aggiungi (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1))))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmds) (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K (Utility|Operatori|Aggiungi (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1)) 1) (Variabili|Predefinito|OttieniTI))) 0.0)
    (:then
      (Funzionedichiamata|AddCmdKind :K K))))
