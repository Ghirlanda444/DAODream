(fn LootMoney ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Classe|BPContainer|OttieniLMoney (Variabili|Predefinito|OttieniLootBox)) 0)
    (:then
      (Variabili|Predefinito|ImpostaMoney (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniMoney) (Classe|BPContainer|OttieniLMoney (Variabili|Predefinito|OttieniLootBox))))
      (Classe|BPContainer|TakeMoney (Variabili|Predefinito|OttieniLootBox)))))
