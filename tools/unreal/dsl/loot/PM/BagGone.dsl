(fn BagGone ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniLootBox))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Classe|BPContainer|OttieniLook (Variabili|Predefinito|OttieniLootBox)) 5) (Utility|Operatori|Uguale(==) (Utilità|Array|Length (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniLootBox))) 0)) (Utility|Operatori|Uguale(==) (Classe|BPContainer|OttieniLMoney (Variabili|Predefinito|OttieniLootBox)) 0))
    (:then
      (Attore|DestroyActor (Variabili|Predefinito|OttieniLootBox)))))))
