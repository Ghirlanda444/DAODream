(fn SetBagInfo (InBag K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length InBag) (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi K 1) 2))
    (:then
      (Variabili|Predefinito|ImpostaNBagS (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) InBag (Utility|Operatori|Moltiplica K 2))))
      (Variabili|Predefinito|ImpostaNBagN (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) InBag (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 2) 1)))))))
