(fn LootTake (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniLootBox))))
    (:then
      (Funzionedichiamata|InvAdd :Item (Utilità|Array|Ottieni(unacopia) (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniLootBox)) K) :N (Utilità|Array|Ottieni(unacopia) (Classe|BPContainer|OttieniLCounts (Variabili|Predefinito|OttieniLootBox)) K))
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|Append "Took " (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemNames) (Utilità|Array|Ottieni(unacopia) (Classe|BPContainer|OttieniLItems (Variabili|Predefinito|OttieniLootBox)) K))))
      (Classe|BPContainer|TakeOut (Variabili|Predefinito|OttieniLootBox) :K K))))
