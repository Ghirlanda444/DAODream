(fn TalentEffect5 (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90047.0)
    (:then
      (Funzionedichiamata|EffShred :K K))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90048.0)
        (:then
          (Funzionedichiamata|EffHowl :K K))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90015.0)
            (:then
              (Funzionedichiamata|EffOverwhelm :K K))
            (:else
              (Funzionedichiamata|HitFoe :Bonus (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 6)) :Mul (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)) :bOff "false" :bSure "false"))))))))
