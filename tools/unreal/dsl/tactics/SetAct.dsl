(fn SetAct (V)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) V 0)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 3) 2.0)
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 4) 0.0))
    (:else
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 3) (Matematica|Float|SelectFloat 5.0 4.0 (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalUse) V) 2.0)))
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 4) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalIds) V)))))
