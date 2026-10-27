(fn BackOne (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTacWho))
    (:else
      (Classe|BPPlotManager|TrPeek (Variabili|Predefinito|OttieniMgr) :A (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniEnL (Variabili|Predefinito|OttieniMgr)) K))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Classe|BPPlotManager|OttieniPkTgt (Variabili|Predefinito|OttieniMgr)) (Variabili|Ottieniunriferimentoasestesso))
    (:then
      (Variabili|Predefinito|ImpostaTacWho (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniEnL (Variabili|Predefinito|OttieniMgr)) K)))))))
