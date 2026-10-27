(fn MatchTI (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTTargets) (Utility|Operatori|Moltiplica K 2)) (Matematica|Float|SelectFloat 6.0 (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 0)) (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 0)) 100.0)))
    (:then
      (Variabili|Predefinito|ImpostaTI K))))
