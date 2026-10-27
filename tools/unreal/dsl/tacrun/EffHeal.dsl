(fn EffHeal (K)
  (Variabili|Predefinito|ImpostaHealAmt (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniSpellPower) 100.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15))))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTacOn))
    (:then
      (Funzionedichiamata|HealWho :A (Variabili|Predefinito|OttieniTacOn)))
    (:else
      (Funzionedichiamata|HealWho :A (Variabili|Ottieniunriferimentoasestesso)))))
