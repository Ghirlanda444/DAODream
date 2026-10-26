(fn TalentEffect4 (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90017.0)
    (:then
      (Funzionedichiamata|EffGrowl :K K))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica K 18)) 90016.0)
        (:then
          (Funzionedichiamata|EffCharge :K K))
        (:else
          (Funzionedichiamata|TalentEffect5 :K K))))))
