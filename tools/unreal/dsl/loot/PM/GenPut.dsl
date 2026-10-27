(fn GenPut (Item Size)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica Item 6) 0)) 4.0)
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 8) 0.5) (Utility|Operatori|Uguale(==) (Utilità|Array|Length (Variabili|Predefinito|OttieniGItems)) 0))
    (:then
      (Variabili|Predefinito|ImpostaGMoney (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniGMoney) (Matematica|Float|Truncate (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 7) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 7)) 6.0) Size) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 0.4) 0.8))))))))
    (:else
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniGLoot) 8) 0.5) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniGMoney) 0))
    (:then
      (Funzionedichiamata|GenStack :Size Size)
      (Funzionedichiamata|GAdd :Item Item :N (Variabili|Predefinito|OttieniGSn)))))))
