(fn TalentEffect3 (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 803.0)
    (:then
      (Funzionedichiamata|EffPin :K K))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 3072.0)
        (:then
          (Funzionedichiamata|EffShatter :K K))
        (:else
          (Funzionedichiamata|HitFoe :Bonus (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 6)) :Mul (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)) :bOff "false" :bSure "false"))))))
