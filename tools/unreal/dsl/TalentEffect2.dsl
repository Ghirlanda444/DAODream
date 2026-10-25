(fn TalentEffect2 (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 0)) 3025.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 0)) 4.0))
    (:then
      (Funzionedichiamata|EffSunder :K K))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 0)) 3.0)
        (:then
          (Funzionedichiamata|EffCritical :K K))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 0)) 3026.0)
            (:then
              (Funzionedichiamata|EffBelt :K K))
            (:else
              (Funzionedichiamata|HitFoe :Bonus (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 6)) :Mul (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 15)) :bOff "false" :bSure "false"))))))))
