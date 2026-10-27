(fn MatchItemAb (R K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniItemStats (Variabili|Predefinito|OttieniMgr)) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 6) 1)) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 4)))
    (:then
      (Variabili|Predefinito|ImpostaSAct (Utilità|Stringa|Append "Use item: " (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniItemNames (Variabili|Predefinito|OttieniMgr)) K))))))
