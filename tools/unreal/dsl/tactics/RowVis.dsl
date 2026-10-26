(fn RowVis (R)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) R (Matematica|Intero|Min(Integer) (Variabili|Predefinito|OttieniSlots) 12))
    (:then
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRowBs) R) "Visible"))
    (:else
      (Widget|SetVisibility (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRowBs) R) "Collapsed"))))
