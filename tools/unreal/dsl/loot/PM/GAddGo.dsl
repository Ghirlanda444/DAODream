(fn GAddGo (Item N)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniGAt) 0)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniGCounts) (Variabili|Predefinito|OttieniGAt) (Utility|Operatori|Aggiungi (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGCounts) (Variabili|Predefinito|OttieniGAt)) N)))
    (:else
      (Utilità|Array|Add (Variabili|Predefinito|OttieniGItems) Item)
      (Utilità|Array|Add (Variabili|Predefinito|OttieniGCounts) N))))
